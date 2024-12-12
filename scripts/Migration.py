import pandas as pd
from pymongo import MongoClient
import os
import logging
import tempfile
import Preparation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def mongodb_creation(host = 'mongodb://localhost:27017/', dbName = "healthcare_dataset", collectionName = "healthcare"):
    logging.info(f"Attempting to connect to MongoDB at {host}")
    try:
        client = MongoClient(host)
        logging.info("Successfully connected to MongoDB server.")
        
        db = client[dbName]
        collection = db[collectionName]
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

    # Read MongoDB connection details from environment variables
    mongoHost = os.getenv('MONGO_HOST', 'localhost')   # dans docker, on utilisera mongodb
    mongoPort = os.getenv('MONGO_PORT', 27017)     
    host = f"mongodb://{mongoHost}:{mongoPort}/"
    dbName = os.getenv('MONGO_DB', 'healthcare_dataset')
    collectionName = 'healthcare'
    script_dir = os.path.dirname(os.path.abspath(__file__)) # emplacement du script
    project_root = os.path.dirname(script_dir)  # on remonte d'un niveau pour avoir la dossier du projet

    clean = False # données déjà pretes ?
    write = False # enregistrer les données nettoyées : deux variables pour éviter de reprocess les données en dev
    clean_data_path = os.path.join(project_root, 'data_clean', 'healthcare_dataset_clean.csv')

    if clean:
        data = pd.read_csv(clean_data_path)
    else:
        data_path = os.path.join(project_root, 'data', 'healthcare_dataset.csv')
        data = Preparation.data_prep(data_path)
        if write:
            data.to_csv(clean_data_path, index=False)
            logging.info(f"Clean data saved to {clean_data_path}")
    
    collection = mongodb_creation(host = host, dbName = dbName, collectionName = collectionName)
    index_creation(collection, ["Name", "Date_of_Admission"], ["Medical_Condition", "Doctor", "Hospital"])
    insert_data(data, collection)
    logging.info("Script ended.")
