"""
Configuration de l'application Personal Finance Manager
"""

import os
from datetime import timedelta

class Config:
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'finance-app-secret-key-change-in-production'
    
    # Base de données (JSON)
    DATA_FILE = os.path.join('data', 'finance_data.json')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    
    # Application
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # Upload (si nécessaire plus tard)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Devise par défaut
    DEFAULT_CURRENCY = 'USD'
    
    # Pagination
    TRANSACTIONS_PER_PAGE = 50
    
    @staticmethod
    def init_app(app):
        """Initialiser la configuration avec l'app Flask"""
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    DATA_FILE = ':memory:'  # Base de données en mémoire pour les tests

# Configuration par environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}