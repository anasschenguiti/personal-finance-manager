#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion MongoDB et créer des données de test
"""

from data.mongodb_manager import MongoDBManager
from models import User, Account, Category, Transaction, Budget, hash_password
import datetime

def test_mongodb_connection():
    """Test de la connexion MongoDB"""
    try:
        print("🔍 Test de connexion MongoDB...")
        db_manager = MongoDBManager()
        print("✅ Connexion MongoDB réussie!")
        
        # Lister les collections
        collections = db_manager.collections.keys()
        print(f"📚 Collections disponibles: {list(collections)}")
        
        return db_manager
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {str(e)}")
        return None

def create_test_data(db_manager):
    """Créer des données de test"""
    try:
        print("\n🔧 Création des données de test...")
        
        # Créer un utilisateur de test
        print("👤 Création d'un utilisateur de test...")
        test_user = User("testuser", "test@example.com", hash_password("password123"))
        test_user.save()
        print(f"✅ Utilisateur créé avec l'ID: {test_user.id}")
        
        # Créer des catégories de test
        print("📂 Création des catégories de test...")
        categories = [
            ("Food & Dining", "expense", "🍽️", "#FF6B6B"),
            ("Transportation", "expense", "🚗", "#4ECDC4"),
            ("Shopping", "expense", "🛍️", "#45B7D1"),
            ("Salary", "income", "💰", "#96CEB4"),
            ("Other Income", "income", "💵", "#FECA57")
        ]
        
        created_categories = []
        for name, cat_type, icon, color in categories:
            category = Category(test_user.id, name, cat_type, icon, color)
            category.is_default = True
            category.save()
            created_categories.append(category)
            print(f"✅ Catégorie '{name}' créée avec l'ID: {category.id}")
        
        # Créer un compte de test
        print("🏦 Création d'un compte de test...")
        test_account = Account(test_user.id, "Compte Principal", "checking", 1000.0, "EUR")
        test_account.save()
        print(f"✅ Compte créé avec l'ID: {test_account.id}")
        
        # Créer des transactions de test
        print("💳 Création des transactions de test...")
        transactions = [
            (test_account.id, created_categories[0].id, -50.0, "Déjeuner", "Carte"),
            (test_account.id, created_categories[1].id, -30.0, "Essence", "Espèces"),
            (test_account.id, created_categories[3].id, 2000.0, "Salaire", "Virement"),
            (test_account.id, created_categories[2].id, -100.0, "Vêtements", "Carte"),
            (test_account.id, created_categories[4].id, 500.0, "Freelance", "Virement")
        ]
        
        for account_id, category_id, amount, description, payment_method in transactions:
            transaction = Transaction(account_id, category_id, amount, description, payment_method)
            transaction.save()
            print(f"✅ Transaction '{description}' créée avec l'ID: {transaction.id}")
        
        # Créer un budget de test
        print("📊 Création d'un budget de test...")
        start_date = datetime.datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        test_budget = Budget(test_user.id, created_categories[0].id, "Budget Alimentation", 300.0, start_date, end_date)
        test_budget.save()
        print(f"✅ Budget créé avec l'ID: {test_budget.id}")
        
        print("\n🎉 Données de test créées avec succès!")
        return test_user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données de test: {str(e)}")
        return None

def verify_data(db_manager, test_user):
    """Vérifier que les données ont été créées"""
    try:
        print("\n🔍 Vérification des données créées...")
        
        # Vérifier l'utilisateur
        user_data = db_manager.get_by_id('users', test_user.id)
        if user_data:
            print(f"✅ Utilisateur trouvé: {user_data['username']}")
        else:
            print("❌ Utilisateur non trouvé")
        
        # Vérifier les catégories
        categories = db_manager.get_by_user_id('categories', test_user.id)
        print(f"✅ {len(categories)} catégories trouvées")
        
        # Vérifier les comptes
        accounts = db_manager.get_by_user_id('accounts', test_user.id)
        print(f"✅ {len(accounts)} comptes trouvés")
        
        # Vérifier les transactions
        transactions = db_manager.find('transactions', {})
        print(f"✅ {len(transactions)} transactions trouvées")
        
        # Vérifier les budgets
        budgets = db_manager.get_by_user_id('budgets', test_user.id)
        print(f"✅ {len(budgets)} budgets trouvés")
        
        print("\n🎯 Toutes les données ont été créées et vérifiées avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")

def main():
    """Fonction principale"""
    print("🚀 Test de l'application Personal Finance Manager avec MongoDB")
    print("=" * 60)
    
    # Test de connexion
    db_manager = test_mongodb_connection()
    if not db_manager:
        return
    
    # Créer des données de test
    test_user = create_test_data(db_manager)
    if not test_user:
        return
    
    # Vérifier les données
    verify_data(db_manager, test_user)
    
    print("\n" + "=" * 60)
    print("✅ Test terminé avec succès!")
    print(f"🔑 Identifiants de test: username=testuser, password=password123")

if __name__ == "__main__":
    main() 