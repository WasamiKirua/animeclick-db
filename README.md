# AnimeClick.it Manga Scraper

A robust asynchronous web scraper designed to extract manga information from AnimeClick.it. Built with Python, it handles pagination, tag-based browsing, and detailed manga information extraction while respecting the site's resources.

## Features

- 🚀 Asynchronous web scraping with AsyncWebCrawler
- 📚 Complete manga information extraction
- 🏷️ Tag-based manga categorization
- 💾 Structured JSON output
- 🤖 Anti-bot detection measures
- ⏱️ Rate limiting and polite crawling

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/animeclick-manga-scraper.git
cd animeclick-manga-scraper
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The scraper provides two main functions:

### 1. Extract Manga Tags
```python
await process_manga_tags()
```
- Extracts all manga tags from the site
- Creates a master list in `data/manga_tags.json`
- Generates individual tag files in `data/manga_by_tag/`

### 2. Extract Manga Details
```python
await extract_manga_details()
```
- Processes manga from tag files
- Extracts comprehensive information
- Saves individual manga files in `data/manga_details/`

## Data Structure

### Tag Data (`data/manga_by_tag/*.json`)
```json
{
    "tag": "robot",
    "tag_url": "/manga/tags/robot",
    "extraction_date": "2024-02-27T12:00:00",
    "manga_count": 42,
    "manga_list": [
        {
            "href": "/manga/12345/manga-title",
            "title": "Manga Title"
        }
    ]
}
```

### Manga Details (`data/manga_details/*.json`)
```json
{
    "url": "https://www.animeclick.it/manga/12345/manga-title",
    "extraction_date": "2024-02-27T12:00:00",
    "details": {
        "titolo_originale": "Original Japanese Title",
        "titolo_inglese": "English Title",
        "titolo_kanji": "漢字タイトル",
        "nazionalita": "Giappone",
        "casa_editrice": "Publisher Name",
        "storia": "Story Author",
        "disegni": "Artist Name",
        "categorie": ["Shounen", "Seinen"],
        "generi": ["Action", "Adventure"],
        "anno": "2024",
        "volumi": "10",
        "capitoli": "42",
        "stato_patria": "completato",
        "stato_italia": "inedito",
        "serializzato_su": "Magazine Name",
        "tag_generici": ["action", "fantasy"],
        "trama": "Plot summary of the manga..."
    }
}
```

## Technical Details

### Browser Configuration
- Headless mode for efficient operation
- Random user agent rotation
- Anti-detection measures
- Configurable viewport settings

### Extraction Strategy
- Precise CSS selectors for data extraction
- Data cleaning and transformation
- Null value handling
- Error recovery mechanisms

### Rate Limiting
- 2-second delay between manga requests
- 1-second delay between tag requests
- Configurable delay settings

### Error Handling
- Network error recovery
- JSON validation
- Empty result detection
- Continuous operation on individual failures

## Example Data

The repository includes sample data files:

### Tag Examples
- `data/manga_by_tag/(260)_robot.json` - Robot-themed manga
- `data/manga_by_tag/(215)_web-comic.json` - Web comics

### Manga Examples
- `data/manga_details/3-ban-sen-no-campanella.json`
- `data/manga_details/3-banme-no-kareshi.json`
- `data/manga_details/13-club.json`
- `data/manga_details/8tsuki-31nichi-no-long-summer.json`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This scraper is for educational purposes only. Please respect AnimeClick.it's terms of service and robots.txt when using this tool.

