# AnimeClick.it Manga Scraper for Dataset creation (RAG, Text and Sentimental Analysis)

A robust asynchronous web scraper designed to extract manga information from AnimeClick.it. Built with Python, it handles pagination, tag-based browsing, and detailed manga information extraction while respecting the site's resources. Uses Datpulse for proxy management and anti-detection measures.

## Features

- 🚀 Asynchronous web scraping with AsyncWebCrawler
- 📚 Complete manga information extraction
- 🏷️ Tag-based manga categorization
- 💾 Structured JSON and CSV output
- 🤖 Anti-bot detection measures via Datpulse proxies
- ⏱️ Rate limiting and polite crawling
- 🔄 Automatic deduplication of manga entries

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

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your Datpulse API key and other settings
```

## Usage

### 1. Extract Manga Details

```
python main.py
```


### 2. Enrich Manga Details and Generate Dataset (CSV and JSON format)
```
python dataset_maker.py
```


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
        "trama": "Plot summary of the manga..."
    }
}
```
### Manga Enhanced (`data/enhanced_dataset/manga_details/*.json)
```json
{
  "url": "https://www.animeclick.it/manga/59956/1-2-3-de-kimeteageru",
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
  "trama": "Plot summary of the manga..."
  "generi": [
    "Scolastico",
    "Sport"
  ],
  "tag_generici": [
    "club-scolastico",
    "Wrestling"
  ]
}
```

### Dataset Format
The final dataset files contain the following fields for each manga:
- `url`: Unique identifier and source URL
- `titolo_originale`: Original title
- `titolo_inglese`: English title
- `titolo_kanji`: Title in kanji
- `nazionalita`: Nationality/origin
- `casa_editrice`: Publisher
- `storia`: Story author
- `disegni`: Artist
- `anno`: Year of publication
- `stato_patria`: Status in original country
- `stato_italia`: Status in Italy
- `serializzato_su`: Serialization magazine
- `trama`: Plot summary
- `generi`: List og genras
- `tag_generici`: List of genra tags 

## Technical Details

### Browser Configuration
- Headless mode for efficient operation
- Datpulse proxy integration for IP rotation
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
- Proxy rotation via Datpulse

### Error Handling
- Network error recovery
- JSON validation
- Empty result detection
- Continuous operation on individual failures
- Proxy fallback mechanisms

## Environment Variables

The following environment variables are required in the `.env` file:

```
PROXY_USERNAME=YOUR USER
PROXY_PASSWORD=YOUR PASSWORD
PROXY_ADDRESS=gw.dataimpulse.com
PROXY_PORT=823
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This scraper is for educational purposes only. Please respect AnimeClick.it's terms of service and robots.txt when using this tool.

