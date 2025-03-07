import os
import json
import pandas as pd
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_manga_details():
    manga_details = []
    mangas_list = [os.path.join('data/manga_details', f) for f in os.listdir('data/manga_details') if f.endswith('.json')]

    for manga_file in mangas_list:
        with open(manga_file, 'r') as f:
            json_data = json.load(f)
            manga_details.append((json_data, manga_file))
    
    return manga_details

def extract_genres_and_tags(url, driver, first_run=False):
    try:
        print(f"\nExtracting genres and tags for: {url}")
        driver.get(url)
        
        # Handle landing page only on first run
        if first_run:
            try:
                landing_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".header a[href*='manga']"))
                )
                if "continua su AnimeClick" in landing_link.text:
                    print("Landing page detected, clicking continue link...")
                    landing_link.click()
                    time.sleep(2)  # Wait for navigation
            except Exception as e:
                print("No landing page detected, continuing...")
        
        # Additional wait to ensure page is fully loaded
        time.sleep(4)
        
        # Wait for manga details to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".col-xs-12.col-sm-7.col-md-8.col-lg-9 dl.dl-horizontal"))
        )
        
        # Extract genres
        genres = []
        genre_elements = driver.find_elements(By.XPATH, "//dt[text()='Genere']/following-sibling::dd//span[@itemprop='genre']")
        for element in genre_elements:
            genres.append(element.text.strip())
        
        # Extract tags
        tags = []
        tag_elements = driver.find_elements(By.XPATH, "//dt[text()='Tag generici']/following-sibling::dd//a[@itemprop='keywords']")
        for element in tag_elements:
            tags.append(element.text.strip())
        
        print(f"Extracted genres: {genres}")
        print(f"Extracted tags: {tags}")
        print("-" * 80)
        
        return genres, tags
        
    except Exception as e:
        print(f"Error extracting genres and tags for {url}: {str(e)}")
        return [], []

def process_dataset():
    manga_details = extract_manga_details()
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-automation")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Initialize the driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # Create enhanced_dataset directory
        os.makedirs('data/enhanced_dataset/manga_details', exist_ok=True)
        print(f"Created directory: data/enhanced_dataset/manga_details")
        
        for i, manga in enumerate(manga_details):
            print(manga[0]['url'])
            manga_data = {
                'url': manga[0]['url'],
                'titolo_originale': manga[0]['details'].get('titolo_originale', ''),
                'titolo_inglese': manga[0]['details'].get('titolo_inglese', ''),
                'titolo_kanji': manga[0]['details'].get('titolo_kanji', ''),
                'nazionalita': manga[0]['details'].get('nazionalita', ''),
                'casa_editrice': manga[0]['details'].get('casa_editrice', ''),
                'storia': manga[0]['details'].get('storia', ''),
                'disegni': manga[0]['details'].get('disegni', ''),
                'anno': manga[0]['details'].get('anno', ''),
                'stato_patria': manga[0]['details'].get('stato_patria', ''),
                'stato_italia': manga[0]['details'].get('stato_italia', ''),
                'serializzato_su': manga[0]['details'].get('serializzato_su', ''),
                'trama': manga[0]['details'].get('trama', '').replace('Trama:', '')
            }
            
            # Extract genres and tags using Selenium (first_run only for first manga)
            genres, tags = extract_genres_and_tags(manga[0]['url'], driver, first_run=(i == 0))
            manga_data['generi'] = genres
            manga_data['tag_generici'] = tags
            
            # Save individual enhanced JSON file
            manga_id = manga[0]['url'].split('/')[-1]
            json_path = f'data/enhanced_dataset/manga_details/{manga_id}.json'
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(manga_data, f, indent=2, ensure_ascii=False)
                print(f"Saved enhanced details to {json_path}")
            except Exception as e:
                print(f"Error saving enhanced JSON file: {e}")
            
            # Add a small delay between requests
            time.sleep(2)
            
    finally:
        driver.quit()

def create_comprehensive_dataset():
    # Read all enhanced manga details
    enhanced_details = []
    manga_files = [f for f in os.listdir('data/enhanced_dataset/manga_details') if f.endswith('.json')]
    
    for manga_file in manga_files:
        with open(os.path.join('data/enhanced_dataset/manga_details', manga_file), 'r', encoding='utf-8') as f:
            manga_data = json.load(f)
            enhanced_details.append(manga_data)
    
    # Remove duplicates based on URL
    print(f"Total entries before removing duplicates: {len(enhanced_details)}")
    unique_dataset = list({manga['url']: manga for manga in enhanced_details}.values())
    print(f"Total entries after removing duplicates: {len(unique_dataset)}")
    
    # Save comprehensive JSON file
    json_path = 'data/enhanced_dataset/animeclick_manga_dataset_20250228.json'
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(unique_dataset, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved comprehensive JSON file: {json_path}")
    except Exception as e:
        print(f"Error saving comprehensive JSON file: {e}")
    
    # Save comprehensive CSV file
    csv_path = 'data/enhanced_dataset/animeclick_manga_dataset_20250228.csv'
    try:
        df = pd.DataFrame(unique_dataset)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Successfully saved comprehensive CSV file: {csv_path}")
    except Exception as e:
        print(f"Error saving comprehensive CSV file: {e}")

if __name__ == "__main__":
    process_dataset()
    create_comprehensive_dataset()