import pandas as pd
from pymongo import MongoClient
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

data = pd.read_csv(os.path.join(script_dir, 'data', 'healthcare_dataset.csv'))

print(f"Dataset chargé avec {data.shape[0]} lignes et {data.shape[1]} colonnes.")

data.columns = [col.strip().replace(" ", "_") for col in data.columns] #retire espace pour underscore pour une bonne syntaxe
data['Date_of_Admission'] = pd.to_datetime(data['Date_of_Admission'])
data['Discharge_Date'] = pd.to_datetime(data['Discharge_Date'])

print(data.info())

client = MongoClient('mongodb://localhost:27017/')
db = client["healthcare_dataset"]
collection = db["healthcare"]

# Index pour optimiser la vitesse des requetes
collection.create_index([("Name", 1), ("Date_of_Admission", 1)], unique=True) #clé primaire, on considere ici que le prénom/nom est unique, ce qui est généralement le cas, évite les doublons
# Une phase d'exploration a montré que un grand nombre de lignes quasi dupliqués ne présentes en réalité que deux ages différents
collection.create_index("Medical_Condition")
collection.create_index("Doctor")
collection.create_index("Hospital")


data_cleaned = data.drop_duplicates(subset=['Name', 'Date_of_Admission'], keep='first') 
# On drop les dupliqués en gardant la premiere occurence, on pourrait garder que l'age le plus élevé/faible à la place

data_dict = data_cleaned.to_dict("records")
try:
    collection.insert_many(data_dict, ordered=False)
    print(f"{len(data_dict)} documents insérés dans la collection.")
except Exception as e:
    print("Certaines données existent déjà ou une erreur s'est produite :", e)
