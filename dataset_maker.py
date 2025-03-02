import os
import json
import pandas as pd

def extract_manga_details():
    manga_details = []
    mangas_list = [os.path.join('data/manga_details', f) for f in os.listdir('data/manga_details') if f.endswith('.json')]

    for manga_file in mangas_list:
        with open(manga_file, 'r') as f:
            json_data = json.load(f)
            manga_details.append((json_data, manga_file))
    
    return manga_details

if __name__ == "__main__":
    manga_details = extract_manga_details()
    
    dataset = []
    for manga in manga_details:
        print(manga[0]['url'])
        if 'titolo_originale' in manga[0]['details']:
            titolo_originale = manga[0]['details']['titolo_originale']
        else:
            titolo_originale = ''
        if 'titolo_inglese' in manga[0]['details']:
            titolo_inglese = manga[0]['details']['titolo_inglese']
        else:
            titolo_inglese = ''
        if 'titolo_kanji' in manga[0]['details']:
            titolo_kanji = manga[0]['details']['titolo_kanji']
        else:
            titolo_kanji = ''
        if 'nazionalita' in manga[0]['details']:
            nazionalita = manga[0]['details']['nazionalita']
        else:
            nazionalita = ''
        if 'casa_editrice' in manga[0]['details']:
            casa_editrice = manga[0]['details']['casa_editrice']
        else:
            casa_editrice = ''
        if 'storia' in manga[0]['details']:
            storia = manga[0]['details']['storia']
        else:
            storia = ''
        if 'disegni' in manga[0]['details']:
            disegni = manga[0]['details']['disegni']
        else:
            disegni = ''
        if 'anno' in manga[0]['details']:
            anno = manga[0]['details']['anno']
        else:
            anno = ''
        if 'stato_patria' in manga[0]['details']:
            stato_patria = manga[0]['details']['stato_patria']
        else:
            stato_patria = ''
        if 'stato_italia' in manga[0]['details']:
            stato_italia = manga[0]['details']['stato_italia']
        else:
            stato_italia = ''
        if 'serializzato_su' in manga[0]['details']:
            serializzato_su = manga[0]['details']['serializzato_su']
        else:
            serializzato_su = ''
        if 'trama' in manga[0]['details']:
            trama = manga[0]['details']['trama']
        else:
            trama = ''
        
        dataset.append({
            'url': manga[0]['url'],
            'titolo_originale': titolo_originale,
            'titolo_inglese': titolo_inglese,
            'titolo_kanji': titolo_kanji,
            'nazionalita': nazionalita,
            'casa_editrice': casa_editrice,
            'storia': storia,
            'disegni': disegni,
            'anno': anno,
            'stato_patria': stato_patria,
            'stato_italia': stato_italia,
            'serializzato_su': serializzato_su,
            'trama': trama
        })
    
    # Remove duplicates based on URL
    print(f"Total entries before removing duplicates: {len(dataset)}")
    unique_dataset = list({manga['url']: manga for manga in dataset}.values())
    print(f"Total entries after removing duplicates: {len(unique_dataset)}")
    
    # Save JSON file
    with open('animeclick_manga_dataset_20250228.json', 'w', encoding='utf-8') as f:
        json.dump(unique_dataset, f, indent=2, ensure_ascii=False)
    
    # Save CSV file using the deduplicated dataset
    df = pd.DataFrame(unique_dataset)
    df.to_csv('animeclick_manga_dataset_20250228.csv', index=False, encoding='utf-8')
    
    
        