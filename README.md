# 💰 Personal Finance Manager

<p align="center">
  <strong>Application web moderne de gestion des finances personnelles, du suivi budgétaire et de l'analyse des dépenses.</strong>
</p>

<p align="center">
  <a href="#-fonctionnalités-clés"><img src="https://img.shields.io/badge/Status-Actif-success?style=for-the-badge" alt="Status"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.3.3-black.svg?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-4.6+-green.svg?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"></a>
  <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/Tested%20with-pytest-yellow.svg?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest"></a>
  <a href="#-licence"><img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <a href="#-vue-densemble">Vue d'ensemble</a> •
  <a href="#-fonctionnalités-clés">Fonctionnalités</a> •
  <a href="#-stack-technique">Stack Technique</a> •
  <a href="#-structure-du-projet">Architecture</a> •
  <a href="#-installation--démarrage-rapide">Démarrage Rapide</a> •
  <a href="#-tests--vérification">Tests</a> •
  <a href="#-feuille-de-route-roadmap">Roadmap</a>
</p>

---

## 🌟 Vue d'ensemble

**Personal Finance Manager** est une solution web complète développée avec **Flask** et **MongoDB**, conçue pour offrir aux particuliers un contrôle total et intuitif sur leur santé financière. 

L'application permet d'agréger ses comptes bancaires, de catégoriser automatiquement ses flux de trésorerie (revenus et dépenses), de piloter des budgets mensuels avec des alertes dynamiques et de visualiser ses indicateurs clés d'épargne.

> [!TIP]
> Idéal pour suivre vos dépenses quotidiennes, anticiper vos fins de mois et automatiser le calcul de vos économies nettes.

---

## ✨ Fonctionnalités clés

| Module | Description |
| :--- | :--- |
| 🔐 **Authentification Sécurisée** | Inscription, connexion, gestion des sessions sécurisées et chiffrement des mots de passe en SHA-256. |
| 💳 **Gestion Multi-Comptes** | Création et suivi de comptes bancaires (Courant, Épargne, Espèces), calcul automatique des soldes en temps réel. |
| 💸 **Suivi des Transactions** | Enregistrement des flux (revenus/dépenses), filtrage par période/compte et mise à jour dynamique des soldes. |
| 🏷️ **Catégorisation Intelligente** | Gestion complète des catégories avec personnalisation des couleurs et des icônes pour une lecture visuelle immédiate. |
| 🎯 **Budgets & Alertes** | Définition de plafonds de dépenses par catégorie avec calcul de consommation et alertes de dépassement. |
| 📊 **Dashboard Analytique** | Vue synthétique mensuelle : total des revenus, dépenses, taux d'épargne nette et transactions récentes. |
| 🔌 **API Interne RESTful** | Points de terminaison JSON pour interroger l'état des comptes et l'historique financier de manière asynchrone. |

---

## 🛠️ Stack Technique

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     Client      │ ───> │   Flask Core    │ ───> │     MongoDB     │
│ Jinja2 / HTML5  │ <─── │ Python 3.11+    │ <─── │   PyMongo 4.6   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

- **Backend** : [Python 3.11+](https://www.python.org/) & [Flask 2.3.3](https://flask.palletsprojects.com/)
- **Base de données** : [MongoDB](https://www.mongodb.com/) via le driver officiel [PyMongo 4.6.1](https://pymongo.readthedocs.io/)
- **Sécurité** : Hachage cryptographique SHA-256, gestion de sessions HTTP-Only
- **Frontend** : Templates dynamiques Jinja2, HTML5 sémantique, CSS moderne et responsive
- **Tests** : [pytest 7.4.3](https://docs.pytest.org/) & script de seed/validation automatisé

---

## 📂 Structure du projet

```plaintext
financial-trucker-main/
├── app.py                     # Point d'entrée de l'application (serveur Flask)
├── routes.py                  # Contrôleurs, endpoints REST et logique métier
├── models.py                  # Modèles de données (User, Account, Category, etc.)
├── base_models.py             # Classe abstraite de base pour les entités
├── config.py                  # Gestion des configurations (Dev, Prod, Test)
├── requirements.txt           # Dépendances Python du projet
├── test_mongodb.py            # Script d'intégration et d'initialisation de données
├── data/
│   └── mongodb_manager.py     # Couche d'accès aux données (CRUD MongoDB)
├── static/                    # Feuilles de style CSS, scripts JavaScript, médias
└── templates/                 # Vues Jinja2 de l'interface utilisateur
    ├── base.html              # Layout principal (barre de navigation, flash messages)
    ├── landing.html           # Page d'accueil publique
    ├── dashboard.html         # Tableau de bord principal
    ├── accounts.html          # Vue et gestion des comptes
    ├── transactions.html      # Vue et historique des transactions
    ├── categories.html        # Gestion des catégories
    ├── budgets.html           # Suivi et jauges budgétaires
    └── ...                    # Formulaires d'ajout et d'édition
```

---

## 🚀 Installation & Démarrage Rapide

### 📋 Prérequis

- **Python 3.11** ou supérieur installé ([Télécharger Python](https://www.python.org/downloads/))
- **MongoDB** en cours d'exécution localement sur `mongodb://localhost:27017/` ou une instance distante (MongoDB Atlas)

> [!NOTE]
> Si vous utilisez Docker, vous pouvez lancer MongoDB rapidement avec :
> ```bash
> docker run -d -p 27017:27017 --name mongo-finance mongo:latest
> ```

---

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/anasschenguiti/personal-finance-manager.git
cd personal-finance-manager
```

---

### 2️⃣ Créer et activer l'environnement virtuel

<details open>
<summary><b>Windows (PowerShell)</b></summary>

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
</details>

<details>
<summary><b>Linux / macOS (Bash)</b></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
```
</details>

---

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configuration de l'environnement

L'application s'adapte à vos variables d'environnement. Vous pouvez exporter votre clé secrète personnalisée :

```bash
# Optionnel : définir une clé secrète personnalisée
export SECRET_KEY="votre-cle-secrete-ultra-securisee"  # Linux/macOS
$env:SECRET_KEY="votre-cle-secrete-ultra-securisee"    # Windows PowerShell
```

| Variable | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `SECRET_KEY` | Clé de signature des sessions Flask | `finance-app-secret-key-change-in-production` |
| `FLASK_DEBUG` | Mode de débogage Flask (`True` / `False`) | `True` |

---

### 5️⃣ Vérifier et alimenter la base de données (Seed)

Exécutez le script de validation pour tester la connexion MongoDB et créer un jeu de données de test :

```bash
python test_mongodb.py
```

Ce script vérifie :
- ✅ La connectivité au serveur MongoDB
- ✅ La création automatique des collections
- ✅ L'insertion d'un utilisateur de test avec ses comptes, catégories et budgets

---

### 6️⃣ Démarrer l'application

```bash
python app.py
```

Rendez-vous sur votre navigateur à l'adresse suivante :
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Tests & Vérification

Pour exécuter la suite de tests automatisés :

```bash
pytest
```

---

## 🔒 Sécurité & Bonnes Pratiques

> [!IMPORTANT]
> Avant tout déploiement en environnement de production :
> - Définissez une variable d'environnement `SECRET_KEY` forte et aléatoire.
> - Activez `SESSION_COOKIE_SECURE = True` pour forcer le transit des cookies via HTTPS.
> - Restreignez l'accès à votre instance MongoDB avec authentification par identifiant et mot de passe.

---

## 🗺️ Feuille de Route (Roadmap)

- [x] Architecture modulaire Flask + MongoDB
- [x] Authentification & gestion de profils
- [x] Suivi des transactions & mise à jour automatique des soldes
- [x] Budgets mensuels et système d'alertes
- [ ] 📈 Graphiques interactifs (Chart.js) pour l'évolution temporelle
- [ ] 📄 Export de rapports en formats CSV et PDF
- [ ] 💱 Support multidevise avec taux de change en direct
- [ ] 🐳 Configuration complète `docker-compose.yml` (App + MongoDB)
- [ ] 🔐 Authentification à deux facteurs (2FA)

---

## 🤝 Contribution

Les contributions, signalements de bugs et suggestions de fonctionnalités sont les bienvenus !

1. Forkez le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commitez vos modifications (`git commit -m 'feat: Add some AmazingFeature'`)
4. Poussez sur votre branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

---

## 📄 Licence

Ce projet est distribué sous licence libre **MIT**. Consultez le fichier `LICENSE` pour plus de détails.

<p align="center">
  Fait avec ❤️ par l'équipe <strong>Personal Finance Manager</strong>
</p>
