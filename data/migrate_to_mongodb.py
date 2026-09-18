from pymongo import MongoClient
import json
from datetime import datetime
import os

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['finance_app']

# Charger les données JSON
json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finance_data.json')
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Fonction pour convertir les dates en format datetime
def convert_dates(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and ('date' in key.lower() or 'created_at' in key.lower() or 'last_login' in key.lower()):
                try:
                    obj[key] = datetime.fromisoformat(value)
                except ValueError:
                    pass
            elif isinstance(value, (dict, list)):
                convert_dates(value)
    elif isinstance(obj, list):
        for item in obj:
            convert_dates(item)
    return obj

# Convertir les données imbriquées en listes
def convert_to_lists(data):
    collections = {}
    for collection_name, items in data.items():
        collections[collection_name] = list(items.values())
    return collections

# Convertir les dates et préparer les données
converted_data = convert_dates(data)
collections_data = convert_to_lists(converted_data)

# Créer les collections et insérer les données
for collection_name, items in collections_data.items():
    # Supprimer la collection si elle existe déjà
    db[collection_name].drop()
    
    # Insérer les données
    if items:
        db[collection_name].insert_many(items)
        print(f"Collection '{collection_name}' créée avec {len(items)} documents")

print("\nMigration terminée avec succès!") 