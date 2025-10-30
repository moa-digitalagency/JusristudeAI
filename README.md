# 📚 Base de Jurisprudence - Plateforme de Recherche IA Juridique

## 📋 Description

Application web professionnelle de gestion et recherche intelligente de cas de jurisprudence marocaine, propulsée par l'intelligence artificielle. La plateforme permet aux juristes de rechercher efficacement des précédents juridiques, gérer une base de données sécurisée de cas, et obtenir des analyses IA pour leurs plaidoiries.

## ✨ Fonctionnalités Principales

### 🔐 Authentification et Sécurité

#### Système d'Authentification Complet
- **Inscription sécurisée** avec validation de mot de passe (8+ caractères minimum)
- **Connexion par email/mot de passe** avec sessions Flask-Login
- **Validation administrateur** : nouveaux utilisateurs en attente d'approbation
- **Compte test fourni** : admin@jurisprudence.com / Admin123!
- **Protection CSRF** intégrée sur toutes les routes
- **Gestion de rôles** : Utilisateur, Manager, Administrateur

#### Sécurité des Données
- **Chiffrement Fernet** pour toutes les données juridiques sensibles (résumés, textes intégraux)
- **Hashage bcrypt** pour tous les mots de passe
- **Prévention des injections SQL** via SQLAlchemy ORM
- **Clés de chiffrement** gérées via variables d'environnement sécurisées
- **Sessions sécurisées** avec cookies HTTPOnly

### 📊 Gestion de la Jurisprudence

#### Base de Données Robuste
- **PostgreSQL** pour robustesse et scalabilité
- **2970+ cas** de jurisprudence marocaine stockés
- **Support bilingue** : français et arabe
- **20+ champs** par cas : référence, titre, juridiction, dates, thèmes, etc.
- **Chiffrement automatique** des données sensibles
- **Indexes optimisés** pour recherches rapides

#### Visualisation et Navigation
- **Liste paginée** de tous les cas (20 par page)
- **Dashboard** avec les 5 cas les plus récents
- **Page détaillée** pour chaque cas avec toutes les informations
- **Badges colorés** pour catégories et statuts
- **Métadonnées complètes** : tribunal, date, type de décision, chambre

#### Gestion Administrative (CRUD Complet)
- **Création de cas** via formulaire complet
- **Modification** de cas existants avec modale d'édition
- **Suppression** de cas avec confirmation
- **Import en masse** : CSV, Excel, PDF (jusqu'à 200 fichiers)
- **Validation automatique** des données importées
- **Traçabilité** : enregistrement de l'utilisateur créateur

### 🤖 Recherche par Intelligence Artificielle

#### Analyse IA Avancée
- **Intégration OpenRouter API** avec Claude 3.5 Sonnet
- **Analyse contextuelle** des cas avec similarité juridique
- **Recommandations** pour la plaidoirie basées sur les précédents
- **Support bilingue** : analyse en français ET arabe
- **Streaming en temps réel** : affichage progressif de l'analyse
- **Historique chiffré** de toutes les recherches

#### Double Mode de Recherche
- **Mode Texte** : description textuelle du cas à analyser
- **Mode Document** : upload de PDF ou Word (.docx)
- **Extraction automatique** du texte depuis les documents
- **Même précision** d'analyse pour les deux modes
- **Interface à onglets** pour basculer facilement

#### Résultats de Recherche
- **Liste des cas similaires** avec scores de pertinence
- **Raisons de similarité** détaillées pour chaque cas
- **Analyse globale** de la jurisprudence applicable
- **Recommandations stratégiques** pour la défense
- **Affichage formaté** avec badges et sections colorées

### 📥 Import et Extraction de Documents

#### Import PDF en Masse
- **Batch import** : jusqu'à 200 PDFs simultanément
- **Extraction automatique** de tous les champs structurés
- **Support format marocain** : reconnaissance des patterns spécifiques
- **Barre de progression** en temps réel
- **Gestion des erreurs** : rapport détaillé des échecs
- **Prévention des doublons** : vérification de la référence

#### Import PDF Simple
- **Upload unique** avec extraction immédiate
- **Prévisualisation** des données extraites
- **Confirmation manuelle** avant sauvegarde
- **Champs extraits automatiquement** :
  - Référence (obligatoire)
  - Titre et juridiction
  - Dates et numéros de décision
  - Thème et mots-clés
  - Résumés (FR/AR) chiffrés
  - Texte intégral chiffré

### 👨‍💼 Panneau d'Administration

#### Gestion des Utilisateurs
- **CRUD complet** : création, lecture, mise à jour, suppression
- **Filtrage avancé** : tous / en attente / approuvés
- **Actions en masse** : approbation/suspension/suppression
- **Protection** : impossible de modifier son propre compte
- **Informations détaillées** : nom, email, rôle, date d'inscription
- **Badges de statut** : En attente, Approuvé, Administrateur

#### Gestion des Rôles et Permissions
- **Création de rôles** personnalisés
- **Attribution de permissions** granulaires
- **Modification** des rôles existants
- **Suppression** sécurisée avec vérifications
- **Page dédiée** : /admin/roles

#### Statistiques et Métriques
- **Nombre total de cas** dans la base
- **Compteur de recherches** par utilisateur
- **Cas récents** sur le tableau de bord
- **Mise à jour en temps réel**

### 🎨 Interface Utilisateur et Design

#### MOA Design System
- **Bordures pointillées colorées** (3px dotted) - signature visuelle
- **Palette professionnelle** : bleu, vert, violet, cyan, rose, jaune
- **Sections colorées** par catégorie avec effets hover
- **Badges** colorés pour identification rapide
- **Boutons** avec ombres et animations fluides
- **Typographie optimisée** : 0.95rem base, hiérarchie claire

#### Navigation et Pages
- **Navbar responsive** avec logo et liens contextuels
- **Login** : page de connexion avec compte test
- **Register** : inscription avec validation
- **Dashboard** : vue d'ensemble avec statistiques
- **Search** : recherche IA avec double mode
- **Cases** : liste paginée de jurisprudence
- **Case Detail** : détails complets d'un cas
- **Admin** : interface complète à onglets
- **Admin Roles** : gestion des rôles et permissions

#### Responsive Design Mobile
- **Mobile-first** : optimisé pour tous les écrans
- **Media queries** : breakpoints à 768px et 480px
- **Grids adaptatifs** : 1 colonne sur mobile, 2-3 sur desktop
- **Navigation empilée** verticalement sur mobile
- **Tailles ajustées** : polices et padding réduits
- **Boutons pleine largeur** sur petit écran

#### Feedback Utilisateur
- **Alertes colorées** : succès (vert), erreur (rouge), info (bleu), warning (jaune)
- **Indicateurs de chargement** animés pendant les requêtes
- **Messages d'état** clairs et explicites
- **Animations fluides** (0.2-0.3s) pour les transitions
- **Confirmations** pour les actions destructives

### 🔧 API REST Complète

#### Authentification
```
POST   /api/auth/register              - Inscription nouvel utilisateur
POST   /api/auth/login                 - Connexion et création de session
POST   /api/auth/logout                - Déconnexion et destruction de session
GET    /api/auth/me                    - Informations utilisateur connecté
GET    /api/auth/admin/users           - Liste utilisateurs avec filtres
POST   /api/auth/admin/approve/:id     - Approuver un utilisateur
PUT    /api/auth/admin/users/:id       - Mettre à jour un utilisateur
DELETE /api/auth/admin/users/:id       - Supprimer un utilisateur
```

#### Jurisprudence
```
GET    /api/cases                      - Liste paginée des cas (20/page)
GET    /api/cases/:id                  - Détails d'un cas spécifique
POST   /api/cases                      - Créer un nouveau cas (admin)
PUT    /api/cases/:id                  - Modifier un cas existant (admin)
DELETE /api/cases/:id                  - Supprimer un cas (admin)
POST   /api/search                     - Recherche IA par description texte
POST   /api/search-stream              - Recherche IA avec streaming SSE
GET    /api/stats                      - Statistiques utilisateur
```

#### Import/Export
```
POST   /api/batch-import               - Import en masse de PDFs
POST   /api/batch-import/extract-pdf   - Extraction simple d'un PDF
```

#### Rôles et Permissions
```
GET    /api/roles                      - Liste de tous les rôles
POST   /api/roles                      - Créer un nouveau rôle
PUT    /api/roles/:id                  - Modifier un rôle
DELETE /api/roles/:id                  - Supprimer un rôle
```

## 🏗️ Architecture Technique

### Structure du Projet
```
.
├── backend/                        # Code serveur Python
│   ├── app.py                     # Application Flask principale
│   ├── config.py                  # Configuration et variables d'environnement
│   ├── init_roles.py              # Initialisation des rôles système
│   ├── models/                    # Modèles de données SQLAlchemy
│   │   ├── user.py               # Modèle utilisateur avec rôles
│   │   ├── case.py               # Modèle cas de jurisprudence
│   │   └── role.py               # Modèle rôles et permissions
│   ├── routes/                    # Endpoints API
│   │   ├── auth.py               # Authentification et utilisateurs
│   │   ├── cases.py              # Gestion des cas juridiques
│   │   ├── batch_import.py       # Import en masse de PDFs
│   │   └── roles.py              # Gestion des rôles
│   ├── services/                  # Services métier
│   │   ├── ai_service.py         # Intégration OpenRouter API
│   │   └── pdf_extractor.py     # Extraction de données PDF
│   └── utils/                     # Utilitaires
│       ├── encryption.py         # Service de chiffrement Fernet
│       ├── text_cleaner.py       # Nettoyage de texte
│       └── secrets_checker.py    # Validation des secrets
├── frontend/                       # Interface utilisateur
│   ├── static/
│   │   ├── css/
│   │   │   └── moa-design.css   # Design system MOA complet
│   │   └── js/                   # JavaScript côté client
│   │       ├── login.js
│   │       ├── register.js
│   │       ├── dashboard.js
│   │       ├── search.js
│   │       ├── cases.js
│   │       ├── admin_new.js
│   │       └── admin_roles.js
│   └── templates/                 # Templates HTML
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── search.html
│       ├── cases.html
│       ├── case_detail.html
│       ├── admin_new.html
│       └── admin_roles.html
├── uploads/                        # Fichiers uploadés
│   └── pdfs/                      # PDFs importés
├── main.py                         # Point d'entrée
├── requirements.txt                # Dépendances Python
├── pyproject.toml                  # Configuration du projet
├── README.md                       # Cette documentation
├── FEATURES.md                     # Liste détaillée des fonctionnalités
├── CHANGELOG.md                    # Historique des versions
├── GUIDE_IMPORT_PDF.md            # Guide d'import PDF
└── MIGRATION_GUIDE.md             # Guide de migration

```

### Technologies Utilisées

#### Backend
- **Flask 3.1.2** : framework web Python
- **SQLAlchemy 2.0.44** : ORM pour PostgreSQL
- **Flask-Login 0.6.3** : gestion des sessions
- **Flask-Bcrypt 1.0.1** : hashage des mots de passe
- **Flask-CORS 6.0.1** : support CORS
- **Flask-WTF 1.2.2** : protection CSRF
- **Cryptography 46.0.3** : chiffrement Fernet
- **Gunicorn 23.0.0** : serveur WSGI production
- **Requests 2.32.5** : requêtes HTTP vers OpenRouter

#### Traitement de Documents
- **PyPDF2 3.0.1** : extraction de texte PDF
- **python-docx 1.2.0** : lecture de fichiers Word
- **openpyxl 3.1.5** : import/export Excel
- **pandas 2.3.3** : manipulation de données

#### Base de Données
- **PostgreSQL** : base de données relationnelle
- **psycopg2-binary 2.9.11** : adaptateur PostgreSQL

#### Frontend
- **JavaScript Vanilla** : pas de framework lourd
- **CSS personnalisé** : MOA Design System
- **Server-Sent Events (SSE)** : streaming temps réel

## 🚀 Installation et Configuration

### Prérequis
- Python 3.11+
- PostgreSQL
- Compte OpenRouter (pour l'IA)

### Installation

1. **Cloner le projet**
```bash
git clone <repo-url>
cd jurisprudence-platform
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**

Créez ou configurez les secrets Replit suivants :

- `DATABASE_URL` : URL PostgreSQL (fournie automatiquement par Replit)
- `SESSION_SECRET` : clé secrète Flask (générée automatiquement)
- `ENCRYPTION_KEY` : clé Fernet (utilisez l'outil de génération)
- `OPENROUTER_API_KEY` : clé API OpenRouter (obtenez-la sur https://openrouter.ai/)

**Générer une clé de chiffrement :**
```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

4. **Initialiser la base de données**

Les tables sont créées automatiquement au démarrage. Un compte administrateur par défaut est créé :
- Email : `admin@jurisprudence.com`
- Mot de passe : `Admin123!`

5. **Lancer l'application**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

L'application sera accessible sur `http://0.0.0.0:5000`

### Configuration de Production

Pour déployer en production :

1. **Changez le mot de passe administrateur**
2. **Utilisez HTTPS** (certificat SSL/TLS)
3. **Configurez gunicorn** avec plusieurs workers :
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
```
4. **Activez les backups** PostgreSQL réguliers
5. **Surveillez les logs** pour détecter les anomalies

## 📊 Modèle de Données

### User (Utilisateur)
```python
id: Integer (PK)
email: String(120) UNIQUE
password_hash: String(256)
first_name: String(64)
last_name: String(64)
is_approved: Boolean (défaut: False)
is_admin: Boolean (défaut: False)
role_id: Integer (FK → Role)
created_at: DateTime
```

### JurisprudenceCase (Cas de Jurisprudence)
```python
id: Integer (PK)
ref: String(100) UNIQUE (référence du cas)
titre: String(500)
juridiction: String(200)
pays: String(100)
ville: String(100)
numero_decision: String(100)
date_decision: Date
numero_dossier: String(100)
type_decision: String(100)
chambre: String(100)
theme: String(200)
mots_cles: String(500)
base_legale: Text
source: String(200)
resume_francais_encrypted: Text (chiffré)
resume_arabe_encrypted: Text (chiffré)
texte_integral_encrypted: Text (chiffré)
created_by: Integer (FK → User)
created_at: DateTime
```

### Role (Rôle)
```python
id: Integer (PK)
name: String(80) UNIQUE
description: String(255)
permissions: JSON (liste de permissions)
created_at: DateTime
```

### SearchHistory (Historique de Recherche)
```python
id: Integer (PK)
user_id: Integer (FK → User)
query_encrypted: Text (chiffré)
results_count: Integer
created_at: DateTime
```

## 🔑 Configuration OpenRouter

### Obtenir une Clé API

1. Créez un compte sur [OpenRouter](https://openrouter.ai/)
2. Accédez à la section "Keys"
3. Générez une nouvelle clé API
4. Copiez la clé et ajoutez-la aux secrets Replit : `OPENROUTER_API_KEY`

### Modèle IA Utilisé

L'application utilise **Claude 3.5 Sonnet** d'Anthropic via OpenRouter :
- **Modèle** : `anthropic/claude-3.5-sonnet`
- **Précision** : Haute pour l'analyse juridique
- **Contexte** : Jusqu'à 50 cas analysés simultanément
- **Température** : 0.3 (réponses précises et cohérentes)
- **Tokens max** : 3000 par réponse

### Coût Estimé

- ~$0.003 par recherche (3 000 tokens à $0.001/1k tokens)
- Budget recommandé : $10-20/mois pour usage moyen

## 📝 Utilisation

### Pour les Juristes

1. **S'inscrire** via la page `/register`
2. **Attendre l'approbation** de l'administrateur
3. **Se connecter** une fois approuvé
4. **Rechercher des cas** :
   - Via description textuelle OU
   - Upload d'un document PDF/Word
5. **Consulter les résultats** : cas similaires + recommandations
6. **Voir l'historique** de ses recherches

### Pour les Administrateurs

1. **Se connecter** avec le compte admin
2. **Gérer les utilisateurs** :
   - Approuver les inscriptions en attente
   - Modifier les rôles
   - Supprimer les comptes inactifs
3. **Gérer la jurisprudence** :
   - Ajouter de nouveaux cas
   - Importer en masse (CSV, Excel, PDF)
   - Modifier ou supprimer des cas
4. **Gérer les rôles** :
   - Créer des rôles personnalisés
   - Attribuer des permissions
5. **Consulter les statistiques** du système

## 🔒 Sécurité et Confidentialité

### Chiffrement des Données
- **Algorithme** : Fernet (AES 128-bit en mode CBC)
- **Données chiffrées** :
  - Résumés de cas (français et arabe)
  - Texte intégral des décisions
  - Historique de recherches utilisateur
- **Clé de chiffrement** : stockée dans les secrets Replit
- **Rotation** : possibilité de migration avec nouvelle clé

### Authentification
- **Hashage** : bcrypt avec salt automatique
- **Sessions** : Flask-Login avec cookies sécurisés
- **Validation** : email unique, mot de passe fort (8+ caractères)
- **Approbation** : administrateur valide les nouveaux comptes
- **Protection CSRF** : token sur toutes les requêtes POST/PUT/DELETE

### Base de Données
- **Injections SQL** : prévenues par SQLAlchemy ORM
- **Contraintes** : foreign keys, unique constraints
- **Indexes** : optimisation sans compromis de sécurité
- **Backups** : recommandés quotidiennement

### Bonnes Pratiques
- ✅ Ne jamais committer de secrets dans le code
- ✅ Utiliser HTTPS en production
- ✅ Changer le mot de passe admin par défaut
- ✅ Surveiller les logs d'erreurs
- ✅ Limiter les tentatives de connexion (à implémenter)

## 📱 Compatibilité Mobile

L'application est **100% responsive** et optimisée pour :

- **Smartphones** : iPhone, Android (320px - 767px)
- **Tablettes** : iPad, Android tablets (768px - 1023px)
- **Desktop** : tous écrans (1024px+)

### Breakpoints CSS
- **480px** : boutons pleine largeur, navigation empilée
- **768px** : grids 1 colonne, polices réduites, padding ajusté

## 🎯 Roadmap

### Version 1.1 (Actuelle) ✅
- ✅ Authentification et rôles
- ✅ Gestion CRUD de la jurisprudence
- ✅ Recherche IA avec Claude 3.5 Sonnet
- ✅ Import PDF en masse (jusqu'à 200 fichiers)
- ✅ Design system MOA responsive
- ✅ Chiffrement de bout en bout

### Version 1.2 (Prochaine)
- [ ] Export PDF des résultats de recherche
- [ ] Filtres avancés (tribunal, date, catégorie)
- [ ] Notifications email pour approbations
- [ ] Documentation API avec Swagger
- [ ] Tests automatisés (unit + intégration)

### Vision Long Terme
- Application mobile native (iOS/Android)
- OCR avancé pour numérisation de jugements
- Chatbot juridique avec RAG
- Collaboration temps réel entre avocats
- Génération automatique de mémoires

## 📄 Documentation Complémentaire

- **[FEATURES.md](FEATURES.md)** : liste exhaustive de toutes les fonctionnalités
- **[CHANGELOG.md](CHANGELOG.md)** : historique des versions et modifications
- **[GUIDE_IMPORT_PDF.md](GUIDE_IMPORT_PDF.md)** : guide complet d'import de PDFs
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** : guide de migration de données

## 🐛 Support et Contribution

### Signaler un Bug

Créez une issue avec :
1. Description du problème
2. Étapes pour reproduire
3. Comportement attendu vs observé
4. Captures d'écran si applicable

### Contribuer

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📜 Licence

© 2024-2025 - Base de Jurisprudence IA
Développé avec le MOA Design System

---

**Note** : Cette application est conçue pour le système juridique marocain mais peut être adaptée à d'autres juridictions.

Pour toute question : contactez l'administrateur système.
