#!/usr/bin/env python3
"""
Personal Finance Manager - Point d'entrée principal
"""

from flask import Flask
from flask_login import LoginManager
from models import User
from routes import app, db_manager
import os
from bson import ObjectId
from flask.json.provider import JSONProvider
import json

class MongoJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=MongoJSONEncoder)
    
    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def ensure_data_directory():
    """Créer le dossier data s'il n'existe pas"""
    if not os.path.exists('data'):
        os.makedirs('data')

if __name__ == '__main__':
    ensure_data_directory()
    app.json = MongoJSONProvider(app)
    print("🚀 Démarrage de Personal Finance Manager...")
    print("📊 Accédez à l'application sur: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)