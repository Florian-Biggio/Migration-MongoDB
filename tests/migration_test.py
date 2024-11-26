import unittest
import pymongo
import pandas as pd

class TestMigration(unittest.TestCase):
    
    def setUp(self):
        # Connexion à la base MongoDB pour les tests
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['test_db']
        self.collection = self.db['test_collection']

        # Charger un dataset de test (exemple CSV)
        self.data = pd.read_csv('test_data.csv')
    
    def test_document_count(self):
        # Effectuer l'insertion des données de test
        self.collection.insert_many(self.data.to_dict('records'))
        
        # Vérifier que le nombre de documents insérés correspond au nombre d'enregistrements
        self.assertEqual(self.collection.count_documents({}), len(self.data))
    
    def test_data_integrity(self):
        # Récupérer le premier document pour vérifier son intégrité
        first_record = self.collection.find_one()
        self.assertIsNotNone(first_record)
        self.assertIn('Name', first_record)  # Vérifier qu'une colonne spécifique existe

    def tearDown(self):
        # Nettoyer la base de données après chaque test
        self.collection.drop()

if __name__ == "__main__":
    unittest.main()
