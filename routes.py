from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import datetime
from functools import wraps
from models import User, Account, Category, Transaction, Budget, hash_password, db_manager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

__all__ = ['app', 'db_manager']

def update_budget_progress_for_category(category_id):
    """Met à jour la progression de tous les budgets pour une catégorie donnée"""
    try:
        # Obtenir tous les budgets pour cette catégorie
        budgets_data = db_manager.find('budgets', {'category_id': category_id})
        
        for budget_data in budgets_data:
            budget = Budget.from_dict(budget_data)
            
            # Calculer le montant dépensé pour ce budget
            budget_transactions = db_manager.find('transactions', {
                'category_id': budget.category_id
            })
            
            spent_amount = 0
            start_date = budget.start_date
            end_date = budget.end_date
            
            # Convertir les dates du budget
            if isinstance(start_date, str):
                start_date_str = start_date
            else:
                start_date_str = start_date.strftime('%Y-%m-%d')
                
            if isinstance(end_date, str):
                end_date_str = end_date
            else:
                end_date_str = end_date.strftime('%Y-%m-%d')
            
            for transaction_data in budget_transactions:
                transaction = Transaction.from_dict(transaction_data)
                transaction_date = transaction.transaction_date
                
                # Convertir transaction_date en format date string
                if isinstance(transaction_date, str):
                    # Si c'est déjà un string ISO, prendre la partie date
                    if 'T' in transaction_date:
                        transaction_date_str = transaction_date.split('T')[0]
                    else:
                        transaction_date_str = transaction_date[:10]
                elif hasattr(transaction_date, 'strftime'):
                    # Si c'est un objet datetime
                    transaction_date_str = transaction_date.strftime('%Y-%m-%d')
                else:
                    # Fallback
                    transaction_date_str = str(transaction_date)[:10]
                
                # Vérifier si la transaction est dans la période du budget et est une dépense
                if (start_date_str <= transaction_date_str <= end_date_str and 
                    transaction.amount < 0):
                    spent_amount += abs(transaction.amount)
            
            # Calculer le pourcentage de progression
            progress_percentage = (spent_amount / budget.amount) * 100 if budget.amount > 0 else 0
            
            # Vérifier les notifications
            if budget.notification != 'none':
                threshold = int(budget.notification)
                if progress_percentage >= threshold:
                    # Ajouter un message flash pour notifier l'utilisateur
                    flash(f'Alerte budget: {budget.name} est à {progress_percentage:.1f}% ({spent_amount:.2f}€/{budget.amount:.2f}€)', 'warning')
    
    except Exception as e:
        print(f"Error updating budget progress: {str(e)}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        user_data = db_manager.get_by_id('users', session['user_id'])
        if user_data:
            return User.from_dict(user_data)
    return None

# Currency symbols mapping
CURRENCY_SYMBOLS = {
    'EUR': '€',
    'USD': '$',
    'GBP': '£',
    'CHF': 'CHF',
    'CAD': 'CAD$',
    'MAD': 'MAD'
}

def get_currency_symbol(currency_code):
    """Retourne le symbole de la devise"""
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)

# Make get_current_user and currency helper available in templates
@app.context_processor
def utility_processor():
    return dict(
        get_current_user=get_current_user,
        get_currency_symbol=get_currency_symbol
    )

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)
        
        # Find user
        user_data = db_manager.find_one('users', {
            '$or': [
                {'username': username},
                {'email': username}
            ],
            'password_hash': password_hash
        })
        
        if user_data:
            user = User.from_dict(user_data)
            if user.is_active:
                session['user_id'] = user.id
                user.last_login = datetime.datetime.now().isoformat()
                user.save()
                flash('Connexion réussie!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Identifiants invalides', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            password_hash = hash_password(password)
            
            # Check if user exists
            existing_user = db_manager.find_one('users', {
                '$or': [
                    {'username': username},
                    {'email': email}
                ]
            })
            
            if existing_user:
                flash('Le nom d\'utilisateur ou l\'email existe déjà', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User(username, email, password_hash)
            user.save()
            
            # Create default categories
            default_categories = [
                ('Food & Dining', 'expense', '🍽️', '#FF6B6B'),
                ('Transportation', 'expense', '🚗', '#4ECDC4'),
                ('Shopping', 'expense', '🛍️', '#45B7D1'),
                ('Salary', 'income', '💰', '#96CEB4'),
                ('Other Income', 'income', '💵', '#FECA57')
            ]
            
            for name, cat_type, icon, color in default_categories:
                category = Category(user.id, name, cat_type, icon, color)
                category.is_default = True
                category.save()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    user_id = str(user.id)
    user_accounts = [Account.from_dict(acc) for acc in db_manager.get_by_user_id('accounts', user_id)]
    user_transactions = []
    
    for account in user_accounts:
        transactions = db_manager.find('transactions', {'account_id': account.id})
        user_transactions.extend([Transaction.from_dict(t) for t in transactions])
    
    # Calculate totals
    total_balance = sum(acc.current_balance for acc in user_accounts)
    
    # Normalize transaction dates for template compatibility and sorting
    for transaction in user_transactions:
        if isinstance(transaction.transaction_date, str):
            transaction.transaction_date_str = transaction.transaction_date
            # Convert string to datetime for sorting
            try:
                transaction.transaction_date_for_sort = datetime.datetime.fromisoformat(transaction.transaction_date.replace('Z', '+00:00'))
            except:
                transaction.transaction_date_for_sort = datetime.datetime.now()
        else:
            transaction.transaction_date_str = transaction.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')
            transaction.transaction_date_for_sort = transaction.transaction_date
    
    recent_transactions = sorted(user_transactions, 
                               key=lambda x: x.transaction_date_for_sort, reverse=True)[:5]
    
    # Monthly income/expense
    current_month = datetime.datetime.now().strftime('%Y-%m')
    monthly_income = sum(t.amount for t in user_transactions 
                        if t.amount > 0 and t.transaction_date_str.startswith(current_month))
    monthly_expense = sum(abs(t.amount) for t in user_transactions 
                         if t.amount < 0 and t.transaction_date_str.startswith(current_month))
    
    # Monthly savings
    monthly_savings = monthly_income - monthly_expense
    
    # Savings goals
    savings_goals = [
        {'name': 'Emergency Fund', 'amount': 1000},
        {'name': 'Vacation', 'amount': 2000},
        {'name': 'Home Improvement', 'amount': 5000}
    ]
    
    # Budgets
    user_budgets = [Budget.from_dict(b) for b in db_manager.get_by_user_id('budgets', user_id)]
    
    # Category labels and values
    categories = [Category.from_dict(c) for c in db_manager.get_by_user_id('categories', user_id)]
    category_labels = [c.name for c in categories]
    category_values = [
        sum(t.amount for t in user_transactions if t.category_id == c.id and t.amount > 0)
        for c in categories
    ]
    
    return render_template('dashboard.html',
                         user=user,
                         accounts=user_accounts,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         monthly_savings=monthly_savings,
                         savings_goals=savings_goals,
                         budgets=user_budgets,
                         category_labels=category_labels,
                         category_values=category_values)

@app.route('/accounts')
@login_required
def accounts():
    user = get_current_user()
    user_id = str(user.id)
    user_accounts = [Account.from_dict(acc) for acc in db_manager.get_by_user_id('accounts', user_id)]
    return render_template('accounts.html', accounts=user_accounts)

@app.route('/accounts/add', methods=['GET', 'POST'])
@login_required
def add_account():
    if request.method == 'POST':
        try:
            user = get_current_user()
            user_id = str(user.id)
            name = request.form['name']
            account_type = request.form['type']
            initial_balance = float(request.form['balance'])
            currency = request.form.get('currency', 'USD')
            
            account = Account(user_id, name, account_type, initial_balance, currency)
            account.save()
            
            flash('Account created successfully!', 'success')
            return redirect(url_for('accounts'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_account.html')
    
    return render_template('add_account.html')

@app.route('/transactions')
@login_required
def transactions():
    user = get_current_user()
    user_id = str(user.id)
    user_accounts = [Account.from_dict(acc) for acc in db_manager.get_by_user_id('accounts', user_id)]
    user_transactions = []
    
    for account in user_accounts:
        transactions = db_manager.find('transactions', {'account_id': account.id})
        for t in transactions:
            transaction = Transaction.from_dict(t)
            # Add account and category names for display
            transaction.account_name = account.name
            category_data = db_manager.get_by_id('categories', transaction.category_id)
            if category_data:
                transaction.category_name = Category.from_dict(category_data).name
            else:
                transaction.category_name = 'Unknown'
            
            # Normalize transaction date for template compatibility and sorting
            if isinstance(transaction.transaction_date, str):
                transaction.transaction_date_str = transaction.transaction_date
                # Convert string to datetime for sorting
                try:
                    transaction.transaction_date_for_sort = datetime.datetime.fromisoformat(transaction.transaction_date.replace('Z', '+00:00'))
                except:
                    transaction.transaction_date_for_sort = datetime.datetime.now()
            else:
                transaction.transaction_date_str = transaction.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')
                transaction.transaction_date_for_sort = transaction.transaction_date
            
            user_transactions.append(transaction)
    
    user_transactions.sort(key=lambda x: x.transaction_date_for_sort, reverse=True)
    return render_template('transactions.html', transactions=user_transactions)

@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    user = get_current_user()
    user_id = str(user.id)
    user_accounts = [Account.from_dict(acc) for acc in db_manager.get_by_user_id('accounts', user_id)]
    user_categories = [Category.from_dict(cat) for cat in db_manager.get_by_user_id('categories', user_id)]
    
    if request.method == 'POST':
        try:
            account_id = request.form['account_id']
            category_id = request.form['category_id']
            amount = float(request.form['amount'])
            description = request.form['description']
            payment_method = request.form.get('payment_method', '')
            
            transaction = Transaction(account_id, category_id, amount, description, payment_method)
            transaction.save()
            
            # Update account balance
            account_data = db_manager.get_by_id('accounts', account_id)
            if account_data:
                account = Account.from_dict(account_data)
                account.current_balance += amount
                account.save()
            
            # Mettre à jour la progression des budgets pour cette catégorie
            update_budget_progress_for_category(category_id)
            
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('transactions'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_transaction.html', 
                                 accounts=user_accounts,
                                 categories=user_categories)
    
    return render_template('add_transaction.html', 
                         accounts=user_accounts,
                         categories=user_categories)

@app.route('/categories')
@login_required
def categories():
    user = get_current_user()
    user_id = str(user.id)
    user_categories = [Category.from_dict(cat) for cat in db_manager.get_by_user_id('categories', user_id)]
    return render_template('categories.html', categories=user_categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        try:
            user = get_current_user()
            user_id = str(user.id)
            name = request.form['name']
            category_type = request.form['type']
            icon = request.form.get('icon', '')
            color = request.form.get('color', '#000000')
            
            category = Category(user_id, name, category_type, icon, color)
            category.save()
            
            flash('Category created successfully!', 'success')
            return redirect(url_for('categories'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_category.html')
    
    return render_template('add_category.html')

@app.route('/budgets')
@login_required
def budgets():
    user = get_current_user()
    user_id = str(user.id)
    user_budgets = [Budget.from_dict(b) for b in db_manager.get_by_user_id('budgets', user_id)]
    user_categories = [Category.from_dict(cat) for cat in db_manager.get_by_user_id('categories', user_id)]
    
    # Add category objects and calculate spent amounts for budgets
    for budget in user_budgets:
        category_data = db_manager.get_by_id('categories', budget.category_id)
        if category_data:
            budget.category = Category.from_dict(category_data)
        else:
            # Create a default category object
            budget.category = Category(user_id, 'Unknown', 'expense', '❓', '#888888')
            budget.category.name = 'Unknown'
        
        # Normalize dates to strings for template compatibility
        if isinstance(budget.start_date, str):
            budget.start_date_str = budget.start_date
        else:
            budget.start_date_str = budget.start_date.strftime('%Y-%m-%d')
            
        if isinstance(budget.end_date, str):
            budget.end_date_str = budget.end_date
        else:
            budget.end_date_str = budget.end_date.strftime('%Y-%m-%d')
        
        # Calculate spent amount for this budget
        # Get all transactions for this category in the budget period
        budget_transactions = db_manager.find('transactions', {
            'category_id': budget.category_id
        })
        
        # Filter transactions by date range and calculate spent amount
        spent_amount = 0
        start_date = budget.start_date
        end_date = budget.end_date
        
        for transaction_data in budget_transactions:
            transaction = Transaction.from_dict(transaction_data)
            transaction_date = transaction.transaction_date
            
            # Convert dates to comparable format
            if isinstance(start_date, str):
                start_date_str = start_date
            else:
                start_date_str = start_date.strftime('%Y-%m-%d')
                
            if isinstance(end_date, str):
                end_date_str = end_date
            else:
                end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Convertir transaction_date en format date string
            if isinstance(transaction_date, str):
                # Si c'est déjà un string ISO, prendre la partie date
                if 'T' in transaction_date:
                    transaction_date_str = transaction_date.split('T')[0]
                else:
                    transaction_date_str = transaction_date[:10]
            elif hasattr(transaction_date, 'strftime'):
                # Si c'est un objet datetime
                transaction_date_str = transaction_date.strftime('%Y-%m-%d')
            else:
                # Fallback
                transaction_date_str = str(transaction_date)[:10]
            
            # Check if transaction is in budget period and is an expense
            if (start_date_str <= transaction_date_str <= end_date_str and 
                transaction.amount < 0):
                spent_amount += abs(transaction.amount)
        
        budget.spent = spent_amount
    
    return render_template('budgets.html', budgets=user_budgets, categories=user_categories)

@app.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    user = get_current_user()
    user_id = str(user.id)
    user_categories = [Category.from_dict(cat) for cat in db_manager.get_by_user_id('categories', user_id)]
    
    if request.method == 'POST':
        try:
            category_id = request.form['category_id']
            name = request.form['name']
            amount = float(request.form['amount'])
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            recurrent = request.form.get('recurrent', 'no')
            notification = request.form.get('notification', 'none')
            
            budget = Budget(user_id, category_id, name, amount, start_date, end_date)
            budget.recurrent = recurrent
            budget.notification = notification
            budget.save()
            
            flash('Budget created successfully!', 'success')
            return redirect(url_for('budgets'))
        except ValueError as e:
            flash(str(e), 'error')
            # Calculer les dates par défaut
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            end_of_month = datetime.datetime.now().replace(day=1)
            if end_of_month.month == 12:
                end_of_month = end_of_month.replace(year=end_of_month.year + 1, month=1)
            else:
                end_of_month = end_of_month.replace(month=end_of_month.month + 1)
            end_of_month = (end_of_month - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            return render_template('add_budget.html', categories=user_categories, today=today, end_of_month=end_of_month)
    
    # Calculer les dates par défaut
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    end_of_month = datetime.datetime.now().replace(day=1)
    if end_of_month.month == 12:
        end_of_month = end_of_month.replace(year=end_of_month.year + 1, month=1)
    else:
        end_of_month = end_of_month.replace(month=end_of_month.month + 1)
    end_of_month = (end_of_month - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('add_budget.html', categories=user_categories, today=today, end_of_month=end_of_month)

@app.route('/budgets/edit/<budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    user = get_current_user()
    user_id = str(user.id)
    user_categories = [Category.from_dict(cat) for cat in db_manager.get_by_user_id('categories', user_id)]
    
    budget_data = db_manager.get_by_id('budgets', budget_id)
    if not budget_data:
        flash('Budget not found', 'error')
        return redirect(url_for('budgets'))
    
    budget = Budget.from_dict(budget_data)
    if budget.user_id != user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('budgets'))
    
    if request.method == 'POST':
        try:
            budget.category_id = request.form['category_id']
            budget.name = request.form['name']
            budget.amount = float(request.form['amount'])
            budget.start_date = request.form['start_date']
            budget.end_date = request.form['end_date']
            budget.recurrent = request.form.get('recurrent', 'no')
            budget.notification = request.form.get('notification', 'none')
            
            budget.save()
            
            flash('Budget updated successfully!', 'success')
            return redirect(url_for('budgets'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('edit_budget.html', 
                                 budget=budget,
                                 categories=user_categories)
    
    return render_template('edit_budget.html', 
                         budget=budget,
                         categories=user_categories)

@app.route('/budgets/delete/<budget_id>', methods=['GET'])
@login_required
def delete_budget(budget_id):
    user = get_current_user()
    user_id = str(user.id)
    budget_data = db_manager.get_by_id('budgets', budget_id)
    
    if not budget_data:
        flash('Budget not found', 'error')
        return redirect(url_for('budgets'))
    
    budget = Budget.from_dict(budget_data)
    if budget.user_id != user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('budgets'))
    
    budget.delete()
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets'))

@app.route('/accounts/edit/<account_id>', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """Page d'édition d'un compte"""
    user = get_current_user()
    user_id = str(user.id)
    
    # Récupérer le compte à modifier
    account_data = db_manager.get_by_id('accounts', account_id)
    if not account_data:
        flash('Compte introuvable!', 'error')
        return redirect(url_for('accounts'))
    
    account = Account.from_dict(account_data)
    
    # Vérifier que le compte appartient à l'utilisateur actuel
    if account.user_id != user_id:
        flash('Accès non autorisé!', 'error')
        return redirect(url_for('accounts'))
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            name = request.form.get('name')
            account_type = request.form.get('type')
            initial_balance = float(request.form.get('initial_balance', 0))
            currency = request.form.get('currency', 'EUR')
            
            # Validation
            if not name or not account_type:
                flash('Tous les champs obligatoires doivent être remplis!', 'error')
                return render_template('edit_account.html', account=account)
            
            # Calculer la différence de solde si le solde initial a changé
            balance_difference = initial_balance - account.initial_balance
            
            # Mettre à jour le compte
            account.name = name
            account.type = account_type
            account.initial_balance = initial_balance
            account.current_balance += balance_difference  # Ajuster le solde actuel
            account.currency = currency
            account.save()
            
            flash('Compte modifié avec succès!', 'success')
            return redirect(url_for('accounts'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('edit_account.html', account=account)
    
    return render_template('edit_account.html', account=account)

@app.route('/accounts/delete/<account_id>', methods=['GET'])
@login_required
def delete_account(account_id):
    user = get_current_user()
    user_id = str(user.id)
    account_data = db_manager.get_by_id('accounts', account_id)
    
    if not account_data:
        flash('Account not found', 'error')
        return redirect(url_for('accounts'))
    
    account = Account.from_dict(account_data)
    if account.user_id != user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('accounts'))
    
    account.delete()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('accounts'))

@app.route('/categories/edit/<category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Page d'édition d'une catégorie"""
    user = get_current_user()
    user_id = str(user.id)
    
    # Récupérer la catégorie à modifier
    category_data = db_manager.get_by_id('categories', category_id)
    if not category_data:
        flash('Catégorie introuvable!', 'error')
        return redirect(url_for('categories'))
    
    category = Category.from_dict(category_data)
    
    # Vérifier que la catégorie appartient à l'utilisateur actuel
    if category.user_id != user_id:
        flash('Accès non autorisé!', 'error')
        return redirect(url_for('categories'))
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            name = request.form.get('name')
            category_type = request.form.get('type')
            icon = request.form.get('icon')
            color = request.form.get('color')
            
            # Validation
            if not name or not category_type or not icon or not color:
                flash('Tous les champs obligatoires doivent être remplis!', 'error')
                return render_template('edit_category.html', category=category)
            
            # Mettre à jour la catégorie
            category.name = name
            category.type = category_type
            category.icon = icon
            category.color = color
            category.save()
            
            flash('Catégorie modifiée avec succès!', 'success')
            return redirect(url_for('categories'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('edit_category.html', category=category)
    
    return render_template('edit_category.html', category=category)

@app.route('/categories/delete/<category_id>', methods=['GET'])
@login_required
def delete_category(category_id):
    user = get_current_user()
    user_id = str(user.id)
    category_data = db_manager.get_by_id('categories', category_id)
    
    if not category_data:
        flash('Category not found', 'error')
        return redirect(url_for('categories'))
    
    category = Category.from_dict(category_data)
    if category.user_id != user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('categories'))
    
    category.delete()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories'))

@app.route('/transactions/delete/<transaction_id>', methods=['GET'])
@login_required
def delete_transaction(transaction_id):
    user = get_current_user()
    user_id = str(user.id)
    transaction_data = db_manager.get_by_id('transactions', transaction_id)
    
    if not transaction_data:
        flash('Transaction not found', 'error')
        return redirect(url_for('transactions'))
    
    transaction = Transaction.from_dict(transaction_data)
    
    # Vérifier que la transaction appartient à un compte de l'utilisateur
    account_data = db_manager.get_by_id('accounts', transaction.account_id)
    if not account_data or Account.from_dict(account_data).user_id != user_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('transactions'))
    
    # Mettre à jour le solde du compte
    account = Account.from_dict(account_data)
    account.current_balance -= transaction.amount  # Inverser la transaction
    account.save()
    
    # Sauvegarder l'ID de catégorie avant de supprimer la transaction
    category_id = transaction.category_id
    
    transaction.delete()
    
    # Mettre à jour la progression des budgets pour cette catégorie
    update_budget_progress_for_category(category_id)
    
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté avec succès', 'success')
    return redirect(url_for('login'))

@app.route('/api/account_balance/<account_id>')
@login_required
def get_account_balance(account_id):
    account_data = db_manager.get_by_id('accounts', account_id)
    if account_data:
        account = Account.from_dict(account_data)
        if account.user_id == get_current_user().id:
            return jsonify({'balance': account.current_balance})
    return jsonify({'error': 'Account not found'}), 404

@app.route('/api/monthly_data')
@login_required
def get_monthly_data():
    user = get_current_user()
    user_id = str(user.id)
    user_accounts = [Account.from_dict(acc) for acc in db_manager.get_by_user_id('accounts', user_id)]
    user_transactions = []
    
    for account in user_accounts:
        transactions = db_manager.find('transactions', {'account_id': account.id})
        user_transactions.extend([Transaction.from_dict(t) for t in transactions])
    
    # Normalize transaction dates for comparison
    for transaction in user_transactions:
        if isinstance(transaction.transaction_date, str):
            transaction.transaction_date_str = transaction.transaction_date
        else:
            transaction.transaction_date_str = transaction.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Get current month's data
    current_month = datetime.datetime.now().strftime('%Y-%m')
    monthly_income = sum(t.amount for t in user_transactions 
                        if t.amount > 0 and t.transaction_date_str.startswith(current_month))
    monthly_expense = sum(abs(t.amount) for t in user_transactions 
                         if t.amount < 0 and t.transaction_date_str.startswith(current_month))
    
    return jsonify({
        'income': monthly_income,
        'expense': monthly_expense,
        'savings': monthly_income - monthly_expense
    })

if __name__ == '__main__':
    app.run(debug=True)