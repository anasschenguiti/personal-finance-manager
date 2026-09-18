import datetime
import uuid
import hashlib
from base_models import BaseModel
from data.mongodb_manager import MongoDBManager

# Initialiser le gestionnaire MongoDB
db_manager = MongoDBManager()

class User(BaseModel):
    def __init__(self, username, email, password_hash):
        super().__init__()
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = True
        self.created_at = datetime.datetime.now().isoformat()
        self.last_login = self.created_at
    
    def to_dict(self):
        return {
            '_id': self.id,
            'id': self.id,  # Ajouter le champ 'id' pour les références
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(data['username'], data['email'], data['password_hash'])
        # Pour les utilisateurs, prioriser le champ 'id' (UUID) car c'est ce qui est utilisé comme référence
        if 'id' in data:
            user.id = data['id']
        elif '_id' in data:
            user.id = data['_id']
        user.is_active = data.get('is_active', True)
        user.created_at = data.get('created_at', datetime.datetime.now().isoformat())
        user.last_login = data.get('last_login', user.created_at)
        return user
    
    def validate(self):
        if not self.username or not self.email or not self.password_hash:
            raise ValueError("Username, email and password are required")
        if '@' not in self.email:
            raise ValueError("Invalid email format")
    
    def save(self, data_manager=None):
        self.validate()
        data = self.to_dict()
        # Vérifier si le document existe déjà dans la base de données
        existing_doc = db_manager.get_by_id('users', self.id)
        if existing_doc:
            db_manager.update('users', self.id, data)
        else:
            self.id = db_manager.create('users', data)
    
    def delete(self, data_manager=None):
        if self.id:
            db_manager.delete('users', self.id)

class Account(BaseModel):
    def __init__(self, user_id, name, account_type, initial_balance, currency="USD"):
        super().__init__()
        self.user_id = user_id
        self.name = name
        self.type = account_type
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.currency = currency
    
    def to_dict(self):
        return {
            '_id': self.id,
            'id': self.id,  # Ajouter le champ 'id' pour les références
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'currency': self.currency,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        account = cls(data['user_id'], data['name'], data['type'], 
                     data['initial_balance'], data['currency'])
        # Pour les comptes, prioriser le champ 'id' (UUID) car c'est ce qui est utilisé comme référence
        if 'id' in data:
            account.id = data['id']
        elif '_id' in data:
            account.id = data['_id']
        account.current_balance = data.get('current_balance', data['initial_balance'])
        account.is_active = data.get('is_active', True)
        account.created_at = data.get('created_at', datetime.datetime.now().isoformat())
        return account
    
    def validate(self):
        if not self.user_id or not self.name or not self.type:
            raise ValueError("User ID, name and type are required")
        if self.initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
    
    def save(self, data_manager=None):
        self.validate()
        data = self.to_dict()
        # Vérifier si le document existe déjà dans la base de données
        existing_doc = db_manager.get_by_id('accounts', self.id)
        if existing_doc:
            db_manager.update('accounts', self.id, data)
        else:
            self.id = db_manager.create('accounts', data)
    
    def delete(self, data_manager=None):
        if self.id:
            db_manager.delete('accounts', self.id)

class Category(BaseModel):
    def __init__(self, user_id, name, category_type, icon="", color="#000000"):
        super().__init__()
        self.user_id = user_id
        self.name = name
        self.type = category_type
        self.icon = icon
        self.color = color
        self.is_default = False
    
    def to_dict(self):
        return {
            '_id': self.id,
            'id': self.id,  # Ajouter le champ 'id' pour les références
            'user_id': self.user_id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'color': self.color,
            'is_default': self.is_default
        }
    
    @classmethod
    def from_dict(cls, data):
        category = cls(data['user_id'], data['name'], data['type'], 
                      data['icon'], data['color'])
        # Pour les catégories, prioriser le champ 'id' (UUID) car c'est ce qui est utilisé comme référence
        if 'id' in data:
            category.id = data['id']
        elif '_id' in data:
            category.id = data['_id']
        category.is_default = data.get('is_default', False)
        return category
    
    def validate(self):
        if not self.user_id or not self.name or not self.type:
            raise ValueError("User ID, name and type are required")
        if self.type not in ['income', 'expense']:
            raise ValueError("Type must be either 'income' or 'expense'")
    
    def save(self, data_manager=None):
        self.validate()
        data = self.to_dict()
        # Vérifier si le document existe déjà dans la base de données
        existing_doc = db_manager.get_by_id('categories', self.id)
        if existing_doc:
            db_manager.update('categories', self.id, data)
        else:
            self.id = db_manager.create('categories', data)
    
    def delete(self, data_manager=None):
        if self.id:
            db_manager.delete('categories', self.id)

class Transaction(BaseModel):
    def __init__(self, account_id, category_id, amount, description="", payment_method=""):
        super().__init__()
        self.account_id = account_id
        self.category_id = category_id
        self.amount = amount
        self.transaction_date = datetime.datetime.now().isoformat()
        self.description = description
        self.is_recurring = False
        self.payment_method = payment_method
    
    def to_dict(self):
        return {
            '_id': self.id,
            'id': self.id,  # Ajouter le champ 'id' pour les références
            'account_id': self.account_id,
            'category_id': self.category_id,
            'amount': self.amount,
            'transaction_date': self.transaction_date,
            'description': self.description,
            'is_recurring': self.is_recurring,
            'payment_method': self.payment_method
        }
    
    @classmethod
    def from_dict(cls, data):
        transaction = cls(data['account_id'], data['category_id'], 
                         data['amount'], data['description'], data['payment_method'])
        # Pour les transactions, prioriser le champ 'id' (UUID) car c'est ce qui est utilisé comme référence
        if 'id' in data:
            transaction.id = data['id']
        elif '_id' in data:
            transaction.id = data['_id']
        transaction.transaction_date = data.get('transaction_date', datetime.datetime.now().isoformat())
        transaction.is_recurring = data.get('is_recurring', False)
        return transaction
    
    def validate(self):
        if not self.account_id or not self.category_id:
            raise ValueError("Account ID and category ID are required")
        if self.amount == 0:
            raise ValueError("Amount cannot be zero")
    
    def save(self, data_manager=None):
        self.validate()
        data = self.to_dict()
        # Vérifier si le document existe déjà dans la base de données
        existing_doc = db_manager.get_by_id('transactions', self.id)
        if existing_doc:
            db_manager.update('transactions', self.id, data)
        else:
            self.id = db_manager.create('transactions', data)
    
    def delete(self, data_manager=None):
        if self.id:
            db_manager.delete('transactions', self.id)

class Budget(BaseModel):
    def __init__(self, user_id, category_id, name, amount, start_date, end_date):
        super().__init__()
        self.user_id = user_id
        self.category_id = category_id
        self.name = name
        self.amount = amount
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = True
        self.recurrent = 'no'  # 'no', 'monthly', 'quarterly', 'yearly'
        self.notification = 'none'  # 'none', '50', '80', '100'
    
    def to_dict(self):
        return {
            '_id': self.id,
            'id': self.id,  # Ajouter le champ 'id' pour les références
            'user_id': self.user_id,
            'category_id': self.category_id,
            'name': self.name,
            'amount': self.amount,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_active': self.is_active,
            'recurrent': self.recurrent,
            'notification': self.notification
        }
    
    @classmethod
    def from_dict(cls, data):
        budget = cls(data['user_id'], data['category_id'], data['name'],
                    data['amount'], data['start_date'], data['end_date'])
        # Pour les budgets, prioriser le champ 'id' (UUID) car c'est ce qui est utilisé comme référence
        if 'id' in data:
            budget.id = data['id']
        elif '_id' in data:
            budget.id = data['_id']
        budget.is_active = data.get('is_active', True)
        budget.recurrent = data.get('recurrent', 'no')
        budget.notification = data.get('notification', 'none')
        return budget
    
    def validate(self):
        if not self.user_id or not self.category_id or not self.name:
            raise ValueError("User ID, category ID and name are required")
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
    
    def save(self, data_manager=None):
        self.validate()
        data = self.to_dict()
        # Vérifier si le document existe déjà dans la base de données
        existing_doc = db_manager.get_by_id('budgets', self.id)
        if existing_doc:
            db_manager.update('budgets', self.id, data)
        else:
            self.id = db_manager.create('budgets', data)
    
    def delete(self, data_manager=None):
        if self.id:
            db_manager.delete('budgets', self.id)

def hash_password(password):
    """Hash un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()