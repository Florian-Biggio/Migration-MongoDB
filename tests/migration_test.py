import os
import logging
import pytest
import pandas as pd
from pymongo import MongoClient
from scripts.Preparation import data_prep  # import de la fonction préparant les données

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read MongoDB connection details from environment variables
mongoHost = os.getenv('MONGO_HOST', 'localhost')
mongoPort = os.getenv('MONGO_PORT', 27017)
host = f"mongodb://{mongoHost}:{mongoPort}/"
dbName = os.getenv('MONGO_DB', 'healthcare_dataset')
collectionName = 'healthcare'

# Paths to data
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_path = os.path.join(project_root, 'data', 'healthcare_dataset.csv')

@pytest.fixture(scope="module")
def mongo_connection():
    """
    Fixture to provide a MongoDB connection to the actual database.
    """
    logging.info(f"Connecting to MongoDB at {host}...")
    client = MongoClient(host=host)
    db = client[dbName]
    collection = db[collectionName]
    logging.info(f"Connected to database: {dbName}, collection: {collectionName}")
    yield collection
    client.close()
    logging.info(f"MongoDB connection closed.")

@pytest.fixture(scope="module")
def preprocessed_data():
    """
    Fixture to preprocess data and return it directly as a DataFrame.
    """
    logging.info(f"Loading data from: {data_path}...")
    processed_data = data_prep(data_path)
    logging.info(f"Data preprocessing completed. Shape: {processed_data.shape}")
    yield processed_data

def test_mongo_connection(mongo_connection):
    """
    Test that the MongoDB instance is running and accessible.
    """
    logging.info("Testing MongoDB connection...")
    assert mongo_connection.database.name == dbName, f"Expected to be connected to {dbName}, but connected to {mongo_connection.database.name}"
    logging.info(f"Successfully connected to the correct database: {dbName}")

def test_data_integrity(mongo_connection, preprocessed_data):
    """
    Test that the data retrieved from MongoDB matches the preprocessed data.
    """
    logging.info("Retrieving data from MongoDB...")
    mongo_data = list(mongo_connection.find({}, {'_id': 0}))
    if len(mongo_data) == 0:
        logging.warning("No data found in MongoDB collection.")
    
    retrieved_data = pd.DataFrame(mongo_data)
    logging.info(f"Retrieved data from MongoDB: {retrieved_data.head()}")

    # Align column order and types
    retrieved_data = retrieved_data[preprocessed_data.columns]
    for column in preprocessed_data.columns:
        if column in retrieved_data.columns:
            retrieved_data[column] = retrieved_data[column].astype(preprocessed_data[column].dtype)
            logging.info(f"Column {column} aligned with the correct data type.")

    try:
        # Compare data
        pd.testing.assert_frame_equal(preprocessed_data, retrieved_data, check_dtype=True)
        logging.info("Data integrity test passed: Preprocessed data matches MongoDB data.")
    except AssertionError as e:
        logging.error(f"Data integrity test failed: {e}")
        raise
