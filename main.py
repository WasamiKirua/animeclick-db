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
            return new Promise((resolve) => {
                // First check if we're on the landing page
                if (window.location.href.includes('trailer.mp4')) {
                    console.log('On landing page...');
                    const link = document.querySelector('.header a[href="/ricerca/manga"]');
                    if (link) {
                        console.log('Clicking manga link...');
                        link.click();
                    }
                }
                resolve(true);
            });
        """,
        wait_for="""
            () => {
                console.log('Current URL:', window.location.href);
                
                // If we're on the search page
                const form = document.querySelector('#form-ricerca-opera');
                if (form) {
                    console.log('Found search form, submitting...');
                    form.submit();
                    return false;
                }
                
                // Wait for manga details
                const details = document.querySelector('.col-xs-12.col-sm-7.col-md-8.col-lg-9 dl.dl-horizontal');
                console.log('Details element found:', details !== null);
                return details !== null;
            }
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

async def extract_manga_details():
    # Browser Configuration (reusing from extract_manga_tags)
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

    # Create directory for manga details
    os.makedirs('data/manga_details', exist_ok=True)

    # Define schemas for manga details extraction
    details_schema = {
        "name": "Manga Details",
        "baseSelector": "#dettagli",  # This is the parent div containing both sections
        "fields": [
            {
                "name": "titolo_originale",
                "selector": "dl.dl-horizontal dt:contains('Titolo originale') + dd span[itemprop='name']",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "titolo_inglese",
                "selector": "dl.dl-horizontal dt:contains('Titolo inglese') + dd span[itemprop='name']",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "titolo_kanji",
                "selector": "dl.dl-horizontal dt:contains('Titolo Kanji') + dd span[itemprop='name']",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "nazionalita",
                "selector": "dl.dl-horizontal dt:contains('Nazionalità') + dd span[itemprop='contentLocation'] span[itemprop='name']",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "casa_editrice",
                "selector": "dl.dl-horizontal dt:contains('Casa Editrice') + dd span[itemprop='creator'] span[itemprop='name'] a",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "storia",
                "selector": "dl.dl-horizontal dt:contains('Storia') ~ dd span[itemprop='name'] a",
                "type": "text",
                "defaultValue": None,
                "transform": lambda values: ", ".join(values) if isinstance(values, list) else values
            },
            {
                "name": "disegni",
                "selector": "dl.dl-horizontal dt:contains('Disegni') ~ dd span[itemprop='name'] a",
                "type": "text",
                "defaultValue": None,
                "transform": lambda values: ", ".join(values) if isinstance(values, list) else values
            },
            {
                "name": "categorie",
                "selector": "dl.dl-horizontal dt:contains('Categoria') + dd a",
                "type": "array",
                "defaultValue": []
            },
            {
                "name": "generi",
                "selector": "dl.dl-horizontal dt:contains('Genere') + dd span[itemprop='genre']",
                "type": "array",
                "defaultValue": []
            },
            {
                "name": "anno",
                "selector": "dl.dl-horizontal dt:contains('Anno') + dd a",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "volumi",
                "selector": "dl.dl-horizontal dt:contains('Volumi') + dd",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "capitoli",
                "selector": "dl.dl-horizontal dt:contains('Capitoli') + dd",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "stato_patria",
                "selector": "dl.dl-horizontal dt:contains('Stato in patria') + dd",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "stato_italia",
                "selector": "dl.dl-horizontal dt:contains('Stato in Italia') + dd",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "disponibilita",
                "selector": "dl.dl-horizontal dt:contains('Disponibilità') + dd span[itemprop='publisher'] span[itemprop='name']",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "serializzato_su",
                "selector": "dl.dl-horizontal dt:contains('Serializzato su') + dd a",
                "type": "text",
                "defaultValue": None
            },
            {
                "name": "tag_generici",
                "selector": "dl.dl-horizontal dt:contains('Tag generici') + dd a",
                "type": "array",
                "defaultValue": []
            },
            {
                "name": "trama",
                "selector": "#trama-div",
                "type": "text",
                "defaultValue": None,
                "transform": lambda value: value.split("Trama:")[1].strip() if value and "Trama:" in value else value
            }
        ]
    }

    details_strategy = JsonCssExtractionStrategy(details_schema)

    # Create config for manga details extraction
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=details_strategy,
        wait_for="""
            () => {
                // Wait for manga details
                const details = document.querySelector('.col-xs-12.col-sm-7.col-md-8.col-lg-9 dl.dl-horizontal');
                console.log('Details element found:', details !== null);
                return details !== null;
            }
        """
    )

    # Process each JSON file in manga_by_tag directory
    manga_by_tag_dir = 'data/manga_by_tag'
    for filename in os.listdir(manga_by_tag_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(manga_by_tag_dir, filename)
        print(f"\nProcessing manga from {filename}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            tag_data = json.load(f)
            
        manga_list = tag_data.get('manga_list', [])
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for manga in manga_list:
                manga_url = f"{manga['href']}"
                print(f"\nVisiting: {manga_url}")
                
                try:
                    print("Making request...")
                    result = await crawler.arun(
                        url=manga_url,
                        config=config
                    )
                    print("Request completed")
                    print(f"Success: {result.success}")
                    
                    if result.success:
                        print("\nRaw HTML content (first 500 chars):")
                        print(result.html[:500])
                        print("\nExtracted content:")
                        print(result.extracted_content)
                        
                        details_list = json.loads(result.extracted_content)
                        details = details_list[0] if details_list else {}
                        
                        # Skip if no details were extracted
                        if not details or all(value is None or value == [] for value in details.values()):
                            print("No details extracted, skipping save...")
                            continue
                            
                        # Create output structure
                        output = {
                            "url": manga_url,
                            "extraction_date": datetime.now().isoformat(),
                            "details": details
                        }
                        
                        manga_id = manga_url.split('/')[-1]
                        details_filepath = f'data/manga_details/{manga_id}.json'
                        
                        with open(details_filepath, 'w', encoding='utf-8') as f:
                            json.dump(output, f, indent=2, ensure_ascii=False)
                        
                        print(f"Saved details to {details_filepath}")
                    else:
                        print(f"Failed to fetch manga page: {result.error_message}")
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"Error processing manga {manga.get('title', manga_url)}: {str(e)}")
                    continue

if __name__ == "__main__":
    # Add the new function to the main execution
    async def main():
        await process_manga_tags()  # Comment this out if you just want to test manga details
        await extract_manga_details()
        print()
        asyncio.run(main())