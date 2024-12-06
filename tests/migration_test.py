import pandas as pd
from pymongo import MongoClient
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# MongoDB connection settings
DATABASE_NAME = 'healthcare_dataset'
COLLECTION_NAME = 'healthcare'

# Read MongoDB connection details from environment variables
mongoHost = os.getenv('MONGO_HOST', 'localhost')   # dans docker, on utilisera mongodb
mongoPort = os.getenv('MONGO_PORT', 27017)     
host = f"mongodb://{mongoHost}:{mongoPort}/"
dbName = os.getenv('MONGO_DB', 'healthcare_dataset')
collectionName = 'healthcare'


script_dir = os.path.dirname(os.path.abspath(__file__)) # emplacement du script
project_root = os.path.dirname(script_dir)  # on remonte d'un niveau pour avoir la dossier du projet
clean_data_path = os.path.join(project_root, 'data_clean', 'healthcare_dataset_clean.csv') # données qu'on upload : csv remanié et nettoyé

def load_cleaned_data(file_path):
    """
    Load the cleaned data from the CSV file used in the main script.
    """
    if not os.path.exists(file_path):
        logging.error(f"Cleaned data file not found at {file_path}")
        return None
    data = pd.read_csv(file_path)
    logging.info(f"Cleaned data loaded from {file_path} with {data.shape[0]} rows.")
    return data

def fetch_data_from_mongodb(collection):
    """
    Fetch all data from the MongoDB collection.
    """
    mongo_data = list(collection.find({}, {'_id': 0})) 
    logging.info(f"Fetched {len(mongo_data)} documents from MongoDB.")
    return pd.DataFrame(mongo_data)

def verify_uploaded_data(cleaned_data, mongodb_data):
    """
    Verify that the data in MongoDB matches the cleaned data.
    """
    # Aligner les colonnes dans le même ordre (MongDB no SQL peut evntuellement changer l'ordre)
    mongodb_data = mongodb_data[cleaned_data.columns]
    # Les types des données peuvent ne pas être conservés, on force donc leur égalité
    for column in cleaned_data.columns:
        if column in mongodb_data.columns:
            mongodb_data[column] = mongodb_data[column].astype(cleaned_data[column].dtype)
    if cleaned_data.equals(mongodb_data):
        logging.info("Verification successful: MongoDB data matches the cleaned dataset.")
    else:
        logging.error("Verification failed: MongoDB data does not match the cleaned dataset.")
        # Montre les différences
        logging.error(f"Expected (Cleaned Data):\n{cleaned_data}")
        logging.error(f"Found in MongoDB:\n{mongodb_data}")

if __name__ == "__main__":
    try:
        cleaned_data = load_cleaned_data(clean_data_path)
        if cleaned_data is None:
            raise FileNotFoundError("Cleaned data file not found. Exiting the script.")

        # Connect to MongoDB
        client = MongoClient(host)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Fetch data from MongoDB
        mongodb_data = fetch_data_from_mongodb(collection)

        # Verification que les données uploadés corespondent à nos données
        verify_uploaded_data(cleaned_data, mongodb_data)

    except Exception as e:
        logging.error("An error occurred during testing: ", exc_info=True)
