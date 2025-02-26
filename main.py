import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
from datetime import datetime
import os
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import time

load_dotenv()

async def extract_manga_tags() -> list[dict]:
    # Browser Configuration
    browser_config = BrowserConfig(
        headless=True,
        viewport_width=1920,
        viewport_height=1080,
        user_agent_mode="random",
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-automation",
            "--disable-dev-shm-usage"
        ]
    )

    # Define schema for tag extraction
    schema = {
        "name": "Manga Tags",
        "baseSelector": "div.panel-body span.label-tag",
        "fields": [
            {
                "name": "href",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "text",
                "selector": "a",
                "type": "text"
            }
        ]
    }

    extraction_strategy = JsonCssExtractionStrategy(schema)

    # Crawler configuration with JavaScript handling
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        js_code="""
            document.querySelector('.header a[href="/ricerca/manga"]').click();
        """,
        wait_for="""
            () => document.querySelector('div.panel-body span.label-tag') !== null
        """
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("Extracting manga tags...")
        result = await crawler.arun(
            url="https://www.animeclick.it/ricerca/manga",
            config=config
        )

        if not result.success:
            print(f"Failed to extract tags: {result.error_message}")
            return []

        # Parse extracted content
        tags_data = json.loads(result.extracted_content)
        
        # Save to JSON file with current date
        output = {
            "extraction_date": datetime.now().isoformat(),
            "tags": tags_data
        }
        
        os.makedirs('data', exist_ok=True)
        with open('data/manga_tags.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully extracted {len(tags_data)} tags")
        return tags_data

def extract_pagination(url: str) -> list[dict]:
    # Proxy configuration
    proxy_username = os.getenv("PROXY_USERNAME")
    proxy_password = os.getenv("PROXY_PASSWORD")
    proxy_address = os.getenv("PROXY_ADDRESS")
    proxy_port = os.getenv("PROXY_PORT")
    
    # Formulate proxy URL
    proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"
    
    # Selenium-wire options for proxy
    seleniumwire_options = {
        "proxy": {
            "http": proxy_url,
            "https": proxy_url
        },
    }
    
    # Chrome options
    options = Options()
    # options.add_argument("--headless=new")  # Uncomment for headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-automation")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    
    try:
        # Initialize Chrome driver with selenium-wire
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            seleniumwire_options=seleniumwire_options,
            options=options
        )
        
        print(f"\nNavigating to {url}")
        driver.get(url)
        
        # Wait for page to be fully loaded
        print("Waiting for page load...")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Handle landing page exactly like crawl4ai
        print("Handling landing page...")
        driver.execute_script("""
            const link = document.querySelector('.header a');
            console.log('Found link:', link);
            if (link) {
                link.click();
                return true;
            }
            return false;
        """)
        
        # Wait for navigation to complete
        print("Waiting for navigation...")
        WebDriverWait(driver, 10).until(
            lambda d: not d.current_url.endswith('trailer.mp4')
        )
        
        # Wait for form to be ready
        print("Waiting for search form...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "form-ricerca-opera"))
        )
        
        # Submit form to trigger search
        print("Submitting search form...")
        driver.execute_script("""
            const form = document.querySelector('#form-ricerca-opera');
            if (form) {
                form.submit();
                return true;
            }
            return false;
        """)
        
        # Wait for pagination to load
        print("Waiting for pagination...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pagination-opera"))
        )
        
        manga_data = {}  # Using dict to store all manga info with title as key
        page_number = 1
        
        while True:
            print(f"\nProcessing page {page_number}")
            
            # Wait for page content to load and stabilize
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "thumbnail-opera-info-extra"))
            )
            # Add small delay to ensure page is stable
            driver.implicitly_wait(1)
            
            try:
                manga_elements = driver.find_elements(By.CLASS_NAME, "thumbnail-opera-info-extra")
                
                for element in manga_elements:
                    try:
                        # Extract title from data-content
                        data_content = element.get_attribute("data-content")
                        if data_content:
                            title_start = data_content.find("<h5>") + 4
                            title_end = data_content.find("</h5>")
                            if title_start > 3 and title_end > 0:
                                title = data_content[title_start:title_end]
                                
                                # Only process if it's a new title
                                if title not in manga_data:
                                    # Find the link and image elements
                                    link_elem = element.find_element(By.CSS_SELECTOR, ".caption a")
                                    img_elem = element.find_element(By.CSS_SELECTOR, "img.img-responsive")
                                    
                                    manga_data[title] = {
                                        "title": title,
                                        "href": link_elem.get_attribute("href"),
                                        "img_src": img_elem.get_attribute("src")
                                    }
                                    print(f"Found manga: {title}")
                                    print(f"  URL: {manga_data[title]['href']}")
                                    print(f"  Image: {manga_data[title]['img_src']}")
                    except Exception as e:
                        print(f"Error extracting manga data: {e}")
                        continue
                
                # Check if next button exists and is clickable
                next_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#pagination-opera .next .page-link"))
                )
                
                if not next_button.is_displayed() or not next_button.is_enabled():
                    print("Next button not available, finishing...")
                    break
                
                print("Clicking next button...")
                # Scroll to button to ensure it's in view
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                
                # Add delay between page clicks
                print("Waiting 2 seconds before next page...")
                time.sleep(5)
                
                # Wait for page content to change using URL or page number instead
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, "#pagination-opera .active").text.strip() == str(page_number + 1)
                )
                
                page_number += 1
                
            except Exception as e:
                print(f"Error processing page: {e}")
                break

        print(f"\nTotal unique manga found: {len(manga_data)}")
        return sorted(list(manga_data.values()), key=lambda x: x['title'])

    except Exception as e:
        print(f"Error during extraction: {e}")
        return []
    finally:
        driver.quit()

async def process_manga_tags():
    # Check if JSON exists, if not extract tags first
    tags = []
    if not os.path.exists('data/manga_tags.json'):
        print("Tags file not found. Extracting tags first...")
        tags = await extract_manga_tags()
    else:
        # Load existing tags from JSON
        with open('data/manga_tags.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags = data.get('tags', [])

    if not tags:
        print("No tags found!")
        return

    # Create directory for manga data
    os.makedirs('data/manga_by_tag', exist_ok=True)

    # Process each tag
    for tag in tags:
        href = tag.get('href', '')
        tag_name = tag.get('text', '').strip()
        if href:
            url = f"https://animeclick.it{href}"
            manga_list = extract_pagination(url)  # Now returns list of dicts
            
            # Create output data structure
            output = {
                "tag": tag_name,
                "tag_url": href,
                "extraction_date": datetime.now().isoformat(),
                "manga_count": len(manga_list),
                "manga_list": manga_list
            }
            
            # Generate filename from tag name (sanitized)
            filename = tag_name.lower().replace(' ', '_').replace('/', '_')
            filepath = f'data/manga_by_tag/{filename}.json'
            
            # Save to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"Tag {tag_name}: Saved {len(manga_list)} manga to {filepath}")
            
            # Add a small delay between requests
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(process_manga_tags())