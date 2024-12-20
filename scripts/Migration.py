import pandas as pd
from pymongo import MongoClient
import os
import logging
import Preparation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def mongodb_creation(host = 'mongodb://localhost:27017/', dbName = "healthcare_dataset", collectionName = "healthcare"):
    logging.info(f"Attempting to connect to MongoDB at {host}")
    try:
        client = MongoClient(host)
        logging.info("Successfully connected to MongoDB server.")
        
        db = client[dbName]
        collection = db[collectionName]
        logging.info(f"Database '{dbName}' and collection '{collectionName}' selected successfully.")
        
        return db, collection
    except Exception as e:
        logging.error("Failed to connect to MongoDB or access the database/collection.", exc_info=True)
        raise

def create_roles_and_users(db):
    logging.info("Setting up roles and users.")
    
    try:
        pass #tester la connection
    except:
        pass

    # Retrieve MongoDB user credentials from environment variables
    admin_user = os.getenv("MONGO_ADMIN_USER", "admin_user")
    admin_password = os.getenv("MONGO_ADMIN_PASS", "admin_password")
    dev_user = os.getenv("MONGO_DEV_USER", "dev_user")
    dev_password = os.getenv("MONGO_DEV_PASS", "dev_password")
    reader_user = os.getenv("MONGO_READER_USER", "reader_user")
    reader_password = os.getenv("MONGO_READER_PASS", "reader_password")

    roles = [
            {
        "role": "AdminRole",
        "privileges": [
            {
                "resource": {"db": "healthcare_dataset", "collection": ""},
                "actions": [
                    "find", "insert", "update", "remove", 
                    "createCollection", "dropCollection", 
                    "collMod", "createIndex", "dropIndex", 
                    "listIndexes", "killCursors"
                ]
            }
        ],
        "roles": [
            { "role": "dbAdmin", "db": "healthcare_dataset" },
            { "role": "userAdmin", "db": "healthcare_dataset" },
            { "role": "readWrite", "db": "healthcare_dataset" }
        ]
    },

        {
            "role": "DevRole",
            "privileges": [
                {"resource": {"db": "healthcare_dataset", "collection": ""}, "actions": ["find", "insert", "update", "remove"]}
            ],
            "roles": [{"role": "readWrite", "db": "healthcare_dataset"}],
        },
        {
            "role": "ReaderRole",
            "privileges": [
                {"resource": {"db": "healthcare_dataset", "collection": ""}, "actions": ["find"]}
            ],
            "roles": [{"role": "read", "db": "healthcare_dataset"}],
        },

    ]

    for role in roles:
        try:
            db.command("createRole", role["role"], privileges=role["privileges"], roles=role["roles"])
            logging.info(f"Role '{role['role']}' created successfully.")
        except Exception as e:
            logging.warning(f"Role '{role['role']}' already exists or could not be created: {e}")
    
    users = [
        {"user": admin_user, "pwd": admin_password, "roles": [{"role": "AdminRole", "db": "healthcare_dataset"}]},
        {"user": dev_user, "pwd": dev_password, "roles": [{"role": "DevRole", "db": "healthcare_dataset"}]},
        {"user": reader_user, "pwd": reader_password, "roles": [{"role": "ReaderRole", "db": "healthcare_dataset"}]},
    ]

    for user in users:
        try:
            db.command("createUser", user["user"], pwd=user["pwd"], roles=user["roles"])
            logging.info(f"User '{user['user']}' created successfully.")
        except Exception as e:
            logging.warning(f"User '{user['user']}' already exists or could not be created: {e}")

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
    mongoHost = os.getenv('MONGO_HOST', 'localhost')
    mongoPort = os.getenv('MONGO_PORT', 27017)
    mongoRootUser = os.getenv('MONGO_INITDB_ROOT_USERNAME', 'admin')
    mongoRootPass = os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'secretpassword')
    host = f"mongodb://{mongoRootUser}:{mongoRootPass}@{mongoHost}:{mongoPort}/"
    #host = f"mongodb://{mongoHost}:{mongoPort}/"


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
    
    db, collection = mongodb_creation(host = host, dbName = dbName, collectionName = collectionName)
    create_roles_and_users(db)
    index_creation(collection, ["Name", "Date_of_Admission"], ["Medical_Condition", "Doctor", "Hospital"])
    insert_data(data, collection)
    logging.info("Script ended.")
