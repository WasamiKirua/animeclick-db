import pandas as pd
import numpy as np
from colorama import Fore, Style

mangas = pd.read_csv('animeclick_manga_dataset_20250228.csv')


from transformers import pipeline

generi = [
    "Arti Marziali", "Avventura", "Azione", "Bambini", "Combattimento", 
    "Commedia", "Crimine", "Cucina", "Demenziale", "Demoni", "Drammatico", 
    "Ecchi", "Erotico", "Fantascienza", "Fantastico", "Fantasy", "Fiaba", 
    "Gang Giovanili", "Gender Bender", "Giallo", "Gioco", "Guerra", "Guro", 
    "Harem", "Hentai", "Horror", "Legal Drama", "Lolicon", "Magia", 
    "Maho Shojo", "Mecha", "Mistero", "Musica", "Parodia", "Politica", 
    "Poliziesco", "Psicologico", "Raccolta", "Reverse-harem", "Scolastico", 
    "Sentimentale", "Shotacon", "Sketch Comedy", "Slice of Life", "Smut", 
    "Soprannaturale", "Sperimentale", "Splatter", "Sport", "Storico", 
    "Supereroi", "Tamarro", "Thriller", "Visual Novel", "Western", 
    "Umorismo", "Violenza", "Antologia"
]


classifier = pipeline("zero-shot-classification",
                model="Jiva/xlm-roberta-large-it-mnli",
                device="mps")

result = classifier(sequence, generi)

print(Fore.GREEN + "--------------------------------" + Style.RESET_ALL)
print(Fore.GREEN + "Genra Classification" + Style.RESET_ALL)
sequence = mangas.loc[0]['trama']
print(Fore.GREEN + sequence + Style.RESET_ALL)
# Get indices of top 3 scores in descending order
top_3_indices = np.argsort(result["scores"])[-3:][::-1]
top_3_labels = [result["labels"][i] for i in top_3_indices]
top_3_scores = [result["scores"][i] for i in top_3_indices]

# Print the top 3 genres with their scores
for label, score in zip(top_3_labels, top_3_scores):
    print(Fore.GREEN + f"{label}: {score:.4f}" + Style.RESET_ALL)



print(Fore.GREEN + "--------------------------------" + Style.RESET_ALL)
print(Fore.GREEN + "Sentimental Analysis" + Style.RESET_ALL)
classifier = pipeline("text-classification",model='MilaNLProc/feel-it-italian-emotion',top_k=4)
prediction = classifier(sequence)

for i in prediction:
    for prediction in i[0:4]:   
        label = prediction["label"]
        score = prediction["score"]
        print(Fore.GREEN + f"{label}:" + Style.RESET_ALL + Fore.CYAN + f" {score*100:.2f}%" + Style.RESET_ALL)



print(Fore.GREEN + "--------------------------------" + Style.RESET_ALL)
print(Fore.GREEN + "Sentimental Analysis" + Style.RESET_ALL)
trama =[mangas.loc[0]['trama']]
print(Fore.GREEN + trama[0] + Style.RESET_ALL)
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("aiknowyou/it-emotion-analyzer")
model = AutoModelForSequenceClassification.from_pretrained("aiknowyou/it-emotion-analyzer")

emotion_analysis = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, top_k=3)
analysis = emotion_analysis(trama)

for i in analysis:
    for prediction in i[0:3]:
        label = prediction["label"]
        label = label.replace("0", "Sadness")
        label = label.replace("1", "Joy")
        label = label.replace("2", "Love")
        label = label.replace("3", "Anger")
        label = label.replace("4", "Fear")
        label = label.replace("5", "Surprise")
        score = prediction["score"]
        print(Fore.GREEN + f"{label}:" + Style.RESET_ALL + Fore.CYAN + f" {score*100:.2f}%" + Style.RESET_ALL)
