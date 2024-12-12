import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def data_prep(data_path):
    '''
    Preparation des données pour la migration mongoDB :
    - Underscore à la place d'un espace
    - Retrait des données dupliquées
    '''
    data = pd.read_csv(data_path)
    logging.info(f"Dataset loaded with {data.shape[0]} rows and {data.shape[1]} columns.")
    
    data.columns = [col.strip().replace(" ", "_") for col in data.columns] # retire espace pour underscore pour une bonne syntaxe
    data['Date_of_Admission'] = pd.to_datetime(data['Date_of_Admission'])
    data['Discharge_Date'] = pd.to_datetime(data['Discharge_Date'])
    
    data = data.drop_duplicates(subset=['Name', 'Date_of_Admission'], keep='first') 
    # On drop les dupliqués en gardant la premiere occurence, on pourrait garder que l'age le plus élevé/faible à la place

    return(data)
