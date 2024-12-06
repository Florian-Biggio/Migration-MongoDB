import pandas as pd
from pymongo import MongoClient
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def data_prep(data_path):
    data = pd.read_csv(data_path)
    logging.info(f"Dataset loaded with {data.shape[0]} rows and {data.shape[1]} columns.")
    
    data.columns = [col.strip().replace(" ", "_") for col in data.columns] # retire espace pour underscore pour une bonne syntaxe
    data['Date_of_Admission'] = pd.to_datetime(data['Date_of_Admission'])
    data['Discharge_Date'] = pd.to_datetime(data['Discharge_Date'])
    
    data = data.drop_duplicates(subset=['Name', 'Date_of_Admission'], keep='first') 
    # On drop les dupliqués en gardant la premiere occurence, on pourrait garder que l'age le plus élevé/faible à la place

    return(data)

def mongodb_creation(host = 'mongodb://localhost:27017/'):
    logging.info(f"Attempting to connect to MongoDB at {host}")
    try:
        client = MongoClient(host)
        logging.info("Successfully connected to MongoDB server.")
        
        db = client["healthcare_dataset"]
        collection = db["healthcare"]
        logging.info("Database 'healthcare_dataset' and collection 'healthcare' selected successfully.")
        
        return collection
    except Exception as e:
        logging.error("Failed to connect to MongoDB or access the database/collection.", exc_info=True)
        raise


def index_creation(collection, 
                   primary_key = ["Name", "Date_of_Admission"], 
                   indexes = ["Medical_Condition", "Doctor", "Hospital"]):
    '''
    Creation d'index selong la clé primaire et les indexes en arguments
    '''
    # Index pour optimiser la vitesse des requetes
    collection.create_index([(key, 1) for key in primary_key], unique=True) # clé primaire, on considere ici que le prénom/nom est unique, ce qui est généralement le cas, évite les doublons
    # Une phase d'exploration a montré que un grand nombre de lignes quasi dupliqués ne présentes en réalité que deux ages différents
    for i in indexes:
        collection.create_index(i)
    logging.info(f"Indexes created for primary key {primary_key} and additional fields {indexes}.")

def insert_data(data, collection):
    data_dict = data.to_dict("records")
    try:
        collection.insert_many(data_dict, ordered=False)
        logging.info(f"{len(data_dict)} documents inserted into the collection.")
    except Exception as e:
        logging.error("Some data already exists or an error occurred: ", exc_info=True)



if __name__ == "__main__":
    logging.info("Script started.")
    clean = True # données déjà pretes ?
    mongoHost = 'mongodb://localhost:27017/'

    script_dir = os.path.dirname(os.path.abspath(__file__)) # emplacement du script
    project_root = os.path.dirname(script_dir)  # on remonte d'un niveau pour avoir la dossier du projet
    
    if clean:
        clean_data_path = os.path.join(project_root, 'data_clean', 'healthcare_dataset_clean.csv')
        data = pd.read_csv(clean_data_path)
    else:
        data_path = os.path.join(project_root, 'data', 'healthcare_dataset.csv')
        data = data_prep(data_path)
        data.to_csv(os.path.join(project_root,'healthcare_dataset_clean.csv'), index=False)
        logging.info(f"Clean data saved to {clean_data_path}")
    
    collection = mongodb_creation(host = mongoHost)
    index_creation(collection, ["Name", "Date_of_Admission"], ["Medical_Condition", "Doctor", "Hospital"])
    insert_data(data, collection)
    logging.info("Script ended.")
