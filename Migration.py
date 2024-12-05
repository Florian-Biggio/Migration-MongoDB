import pandas as pd
from pymongo import MongoClient
import os

def data_prep(data_path):
    data = pd.read_csv(data_path)
    print(f"Dataset chargé avec {data.shape[0]} lignes et {data.shape[1]} colonnes.") #TODO remplacer par LoG
    
    data.columns = [col.strip().replace(" ", "_") for col in data.columns] #retire espace pour underscore pour une bonne syntaxe
    data['Date_of_Admission'] = pd.to_datetime(data['Date_of_Admission'])
    data['Discharge_Date'] = pd.to_datetime(data['Discharge_Date'])
    print(data.info()) #TODO remplacer par LoG
    
    data = data.drop_duplicates(subset=['Name', 'Date_of_Admission'], keep='first') 
    # On drop les dupliqués en gardant la premiere occurence, on pourrait garder que l'age le plus élevé/faible à la place

    return(data)

def mongodb_creation(host = 'mongodb://localhost:27017/'):
    client = MongoClient(host)
    db = client["healthcare_dataset"]
    collection = db["healthcare"]
    return(collection)

def index_creation(collection, 
                   primary_key = ["Name", "Date_of_Admission"], 
                   indexes = ["Medical_Condition", "Doctor", "Hospital"]):
    '''
    The index are created on the collection argument dynamically
    '''
    # Index pour optimiser la vitesse des requetes
    collection.create_index([(key, 1) for key in primary_key], unique=True) #clé primaire, on considere ici que le prénom/nom est unique, ce qui est généralement le cas, évite les doublons
    # Une phase d'exploration a montré que un grand nombre de lignes quasi dupliqués ne présentes en réalité que deux ages différents
    for i in indexes:
        collection.create_index(i)

def insert_data(data, collection):
    data_dict = data.to_dict("records")
    try:
        collection.insert_many(data_dict, ordered=False)
        print(f"{len(data_dict)} documents insérés dans la collection.") #TODO remplacer par LoG
    except Exception as e:
        print("Certaines données existent déjà ou une erreur s'est produite :", e) #TODO remplacer par LoG

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clean = True
    if clean:
        data_path = os.path.join(script_dir, 'data_clean', 'healthcare_dataset_clean.csv')
        data = pd.read_csv(data_path)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(script_dir, 'data', 'healthcare_dataset.csv')
        data = data_prep(data_path)
        data.to_csv(os.path.join(script_dir,'healthcare_dataset_clean.csv'), index=False)
    
    collection = mongodb_creation(host = 'mongodb://localhost:27017/')
    index_creation(collection, ["Name", "Date_of_Admission"], ["Medical_Condition", "Doctor", "Hospital"])
    insert_data(data, collection)
