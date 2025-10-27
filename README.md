# Plateforme de Jurisprudence IA

## 📋 Description

Application web professionnelle pour juristes permettant la recherche intelligente de cas de jurisprudence via l'intelligence artificielle. L'application utilise l'API OpenRouter pour analyser les cas et trouver des précédents similaires dans une base de données sécurisée.

## ✨ Fonctionnalités

### Authentification Sécurisée
- Système d'inscription avec validation par administrateur
- Connexion sécurisée avec mots de passe hashés (bcrypt)
- Sessions utilisateur avec Flask-Login
- Contrôle d'accès basé sur les rôles (utilisateur/admin)

### Gestion de la Jurisprudence
- Base de données PostgreSQL avec plus de 2970 cas
- Toutes les données sensibles sont chiffrées (Fernet encryption)
- Recherche de cas par numéro, titre, catégorie
- Ajout de nouveaux cas par les administrateurs

### Recherche IA
- Analyse intelligente des cas via OpenRouter API
- Identification de précédents similaires
- Recommandations pour la plaidoirie
- Historique des recherches chiffré

### Interface Utilisateur
- Design system MOA professionnel
- Interface fluide et mobile-friendly
- Sections avec bordures pointillées colorées (signature MOA)
- Tailwind CSS pour un design responsive

## 🏗️ Architecture

```
.
├── backend/
│   ├── app.py                 # Application Flask principale
│   ├── config.py              # Configuration et variables d'environnement
│   ├── models/
│   │   ├── user.py           # Modèle utilisateur
│   │   └── case.py           # Modèle cas de jurisprudence
│   ├── routes/
│   │   ├── auth.py           # Routes d'authentification
│   │   └── cases.py          # Routes pour les cas
│   ├── services/
│   │   └── ai_service.py     # Service OpenRouter AI
│   └── utils/
│       └── encryption.py     # Service de chiffrement
└── frontend/
    ├── static/
    │   ├── css/
    │   │   └── moa-design.css    # Design system MOA
    │   └── js/
    │       ├── login.js
    │       ├── register.js
    │       ├── dashboard.js
    │       ├── search.js
    │       └── admin.js
    └── templates/
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── search.html
        └── admin.html
```

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11+
- PostgreSQL
- Clé API OpenRouter

### Variables d'Environnement

Configurez les variables suivantes :

- `DATABASE_URL` : URL de connexion PostgreSQL (déjà configurée)
- `SECRET_KEY` : Clé secrète Flask (générée automatiquement)
- `ENCRYPTION_KEY` : Clé de chiffrement Fernet (générée automatiquement)
- `OPENROUTER_API_KEY` : Clé API OpenRouter (à configurer)

### Installation

1. Les dépendances sont déjà installées via uv
2. La base de données PostgreSQL est configurée
3. Ajoutez votre clé API OpenRouter

### Lancement

```bash
python backend/app.py
```

L'application sera accessible sur `http://0.0.0.0:5000`

## 👤 Compte Administrateur par Défaut

- **Email** : admin@jurisprudence.com
- **Mot de passe** : Admin123!

> ⚠️ **Important** : Changez ce mot de passe en production !

## 🔒 Sécurité

### Chiffrement des Données
- Toutes les données sensibles (descriptions de cas, faits, décisions) sont chiffrées avec Fernet
- Les mots de passe sont hashés avec bcrypt
- Historique des recherches chiffré

### Authentification
- Sessions sécurisées avec Flask-Login
- Validation par administrateur pour nouveaux comptes
- Protection CSRF intégrée

### Base de Données
- Utilisation de PostgreSQL avec SQLAlchemy ORM
- Prévention des injections SQL
- Indexes sur les champs de recherche fréquents

## 📊 Modèle de Données

### User
- id, email, password_hash
- first_name, last_name
- is_approved, is_admin
- created_at

### JurisprudenceCase
- id, case_number, title
- description_encrypted, facts_encrypted, decision_encrypted
- court, date_decision, category, keywords
- created_by, created_at

### SearchHistory
- id, user_id
- query_encrypted, results_count
- created_at

## 🎨 Design System MOA

L'application utilise le design system MOA avec :
- Bordures pointillées colorées (3px dotted)
- Palette de couleurs professionnelle (bleu, vert, violet, etc.)
- Typographie optimisée (0.95rem base)
- Boutons avec effets hover et ombres
- Badges colorés pour les statuts
- Design responsive mobile-first

## 🔧 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Informations utilisateur

### Administration
- `GET /api/auth/admin/users` - Utilisateurs en attente
- `POST /api/auth/admin/approve/<id>` - Approuver un utilisateur

### Cas de Jurisprudence
- `GET /api/cases` - Liste des cas (paginée)
- `GET /api/cases/<id>` - Détails d'un cas
- `POST /api/cases` - Créer un cas (admin)
- `POST /api/search` - Recherche IA

### Statistiques
- `GET /api/stats` - Statistiques utilisateur

## 📝 Utilisation

### Pour les Juristes

1. **Inscription** : Créer un compte (en attente de validation)
2. **Connexion** : Se connecter après approbation
3. **Recherche** : Décrire un cas pour trouver des précédents
4. **Analyse** : Consulter les recommandations de l'IA

### Pour les Administrateurs

1. **Validation** : Approuver les nouveaux utilisateurs
2. **Ajout de cas** : Enrichir la base de jurisprudence
3. **Gestion** : Superviser l'utilisation de la plateforme

## 🔑 Configuration OpenRouter

Pour utiliser la recherche IA, configurez votre clé API OpenRouter :

1. Créez un compte sur [OpenRouter](https://openrouter.ai/)
2. Générez une clé API
3. Ajoutez-la aux secrets Replit : `OPENROUTER_API_KEY`

L'application utilise le modèle `anthropic/claude-3.5-sonnet` pour des analyses juridiques précises.

## 📄 License

© 2024 - Application développée avec le MOA Design System
