# Migration-MongoDB
Migration données médicales vers MongoDB, effectué en python, Conteneurisé dans Docker


## Prérequis Python

- Python 3.x installé
- MongoDB en cours d'exécution (par défaut sur `localhost:27017`)
- Les bibliothèques suivantes installées :
  - `pandas`
  - `pymongo`

Exemple d'installation dans le command prompt avec la commande :

```bash
pip install pandas pymongo
```

Pour lancer la migration et tester qu'elle fonctionne bien :

Toutes les commandes qui suivent sont à lancer à la racine du projet :
### Lancer le script :
```bash
python scripts/migration.py
```
```bash
2024-12-06 16:09:29,106 - INFO - Script started.
2024-12-06 16:09:29,391 - INFO - Attempting to connect to MongoDB at mongodb://localhost:27017/
2024-12-06 16:09:29,399 - INFO - Successfully connected to MongoDB server.
2024-12-06 16:09:29,399 - INFO - Database 'healthcare_dataset' and collection 'healthcare' selected successfully.
2024-12-06 16:09:29,494 - INFO - Indexes created for primary key ['Name', 'Date_of_Admission'] and additional fields ['Medical_Condition', 'Doctor', 'Hospital'].
2024-12-06 16:09:32,781 - INFO - 50000 documents inserted into the collection.
2024-12-06 16:09:32,801 - INFO - Script ended.
```

### Lancer les tests :
```bash
python tests/migration_test.py
```
```bash
2024-12-06 16:19:43,751 - INFO - Cleaned data loaded from Migration-MongoDB\data_clean\healthcare_dataset_clean.csv with 50000 rows.
2024-12-06 16:19:44,161 - INFO - Fetched 50000 documents from MongoDB.
2024-12-06 16:19:44,629 - INFO - Verification successful: MongoDB data matches the cleaned dataset.
```


## Prérequis Docker

- Docker installé. Si ce n'est pas le cas : suivre [le guide d'installation Docker](https://docs.docker.com/get-docker/)
- Docker Compose installé. Instructions [ici](https://docs.docker.com/compose/install/)

## Lancer l'application avec Docker

Follow these steps to run the application using Docker:

### 1. Construire l'image Docker 

```bash
docker-compose build
```

### 2. Lancer les conteneurs Docker

```bash
docker-compose up
```

### 3. Vérifier la Migration

Une fois que les conteneurs sont lancé, la base MongoDB deviennent  accessible aved un client MongoDB tel que MongoDB Compass  
La base de donné est nommée *healthcare_db*

### 4. Arreter les conteneurs Docker
```bash
docker-compose down
```


# Variables d'environnement :

MONGO_HOST : host utilisé, exemple : 'localhost', 'mongodb'  
MONGO_PORT : port utilisé, exemple : 27017  
MONGO_DB : nom de la db, exemple : 'healthcare_dataset'
