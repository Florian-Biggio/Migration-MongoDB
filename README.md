# Migration-MongoDB
Migration données médicales vers MongoDB, Conteneurisé dans Docker


## Prérequis

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
# Lancer le script :
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

# Lancer les tests :
```bash
python tests/migration_test.py
```
```bash
2024-12-06 16:19:43,751 - INFO - Cleaned data loaded from C:\Users\Florian\Desktop\OpenClassrooms\Projet 5\git\Migration-MongoDB\data_clean\healthcare_dataset_clean.csv with 50000 rows.
2024-12-06 16:19:44,161 - INFO - Fetched 50000 documents from MongoDB.
2024-12-06 16:19:44,629 - INFO - Verification successful: MongoDB data matches the cleaned dataset.
```