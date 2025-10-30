# 📖 Documentation Technique - Base de Jurisprudence IA

## Table des Matières

1. [Architecture Système](#architecture-système)
2. [Structure du Projet](#structure-du-projet)
3. [Base de Données](#base-de-données)
4. [API REST](#api-rest)
5. [Services](#services)
6. [Sécurité](#sécurité)
7. [Performance](#performance)
8. [Tests](#tests)

## Architecture Système

### Vue d'Ensemble

L'application suit une architecture **MVC (Model-View-Controller)** adaptée pour Flask :

```
┌─────────────┐
│   Client    │ ← Frontend (HTML/CSS/JS)
│   Browser   │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────┐
│   Nginx     │ ← Reverse Proxy (Production)
│   (Optional)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Gunicorn   │ ← WSGI Server
│   Workers   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Flask    │ ← Application Web
│     App     │
└──────┬──────┘
       │
       ├─────────► Services (AI, PDF, Encryption)
       │
       ├─────────► Routes (API Endpoints)
       │
       └─────────► Models (SQLAlchemy)
                        │
                        ▼
                   PostgreSQL
```

### Flux de Données

1. **Requête entrante** → Nginx (si configuré) → Gunicorn → Flask
2. **Authentification** → Flask-Login vérifie la session
3. **Autorisation** → Décorateurs vérifient les permissions
4. **Traitement** → Route appelle un service si nécessaire
5. **Base de données** → SQLAlchemy ORM gère les requêtes
6. **Réponse** → JSON ou template HTML rendu

## Structure du Projet

### Arborescence Détaillée

```
jurisprudence-platform/
│
├── backend/                        # Code serveur
│   ├── __init__.py
│   ├── app.py                     # Point d'entrée Flask
│   ├── config.py                  # Configuration centrale
│   ├── init_roles.py              # Initialisation rôles
│   │
│   ├── models/                    # Modèles de données
│   │   ├── __init__.py
│   │   ├── user.py               # Modèle User + db
│   │   ├── case.py               # Modèle JurisprudenceCase
│   │   └── role.py               # Modèle Role + Permission
│   │
│   ├── routes/                    # Contrôleurs API
│   │   ├── __init__.py
│   │   ├── auth.py               # /api/auth/* endpoints
│   │   ├── cases.py              # /api/cases/* endpoints
│   │   ├── batch_import.py       # /api/batch-import/* endpoints
│   │   └── roles.py              # /api/roles/* endpoints
│   │
│   ├── services/                  # Logique métier
│   │   ├── __init__.py
│   │   ├── ai_service.py         # Service OpenRouter
│   │   └── pdf_extractor.py     # Service extraction PDF
│   │
│   └── utils/                     # Utilitaires
│       ├── __init__.py
│       ├── encryption.py         # Chiffrement Fernet
│       ├── text_cleaner.py       # Nettoyage texte
│       └── secrets_checker.py    # Vérification secrets
│
├── frontend/                       # Interface utilisateur
│   ├── static/
│   │   ├── css/
│   │   │   └── moa-design.css   # Design system complet
│   │   └── js/
│   │       ├── login.js
│   │       ├── register.js
│   │       ├── dashboard.js
│   │       ├── search.js
│   │       ├── cases.js
│   │       ├── admin_new.js
│   │       └── admin_roles.js
│   │
│   └── templates/                 # Templates Jinja2
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── search.html
│       ├── cases.html
│       ├── case_detail.html
│       ├── admin_new.html
│       └── admin_roles.html
│
├── uploads/                        # Fichiers uploadés
│   └── pdfs/                      # PDFs importés
│       ├── single/                # Imports uniques
│       └── batch_*/               # Imports en masse
│
├── main.py                         # Point d'entrée principal
├── requirements.txt                # Dépendances Python
├── pyproject.toml                  # Configuration projet
├── README.md                       # Documentation utilisateur
├── TECHNICAL_DOCUMENTATION.md      # Ce fichier
└── DEPLOYMENT.md                   # Guide déploiement
```

### Responsabilités des Modules

#### backend/app.py
- Initialisation de l'application Flask
- Configuration des extensions (CORS, CSRF, Login)
- Enregistrement des blueprints
- Gestion du cache HTTP
- Routes de rendu de templates
- Création automatique de la base de données
- Initialisation des rôles système
- Création du compte admin par défaut

#### backend/config.py
```python
class Config:
    SECRET_KEY: str                 # Clé session Flask
    DATABASE_URL: str               # URL PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    ENCRYPTION_KEY: bytes           # Clé Fernet
    OPENROUTER_API_KEY: str         # Clé API OpenRouter
    OPENROUTER_API_URL: str         # URL API OpenRouter
```

#### backend/models/
- **user.py**: Modèle User avec attributs, relations, méthodes
- **case.py**: Modèle JurisprudenceCase avec champs chiffrés
- **role.py**: Modèle Role et Permission avec JSON

#### backend/routes/
- **auth.py**: 8 endpoints d'authentification et gestion utilisateurs
- **cases.py**: 7 endpoints de gestion de jurisprudence + recherche IA
- **batch_import.py**: 2 endpoints d'import PDF (masse + simple)
- **roles.py**: 4 endpoints CRUD pour rôles et permissions

#### backend/services/
- **ai_service.py**: 
  - `find_similar_cases()`: recherche synchrone
  - `find_similar_cases_streaming()`: recherche avec SSE
- **pdf_extractor.py**:
  - `extract_case_from_pdf()`: extraction champs structurés
  - Patterns regex pour format marocain

#### backend/utils/
- **encryption.py**: `EncryptionService` avec encrypt/decrypt
- **text_cleaner.py**: Nettoyage et normalisation de texte
- **secrets_checker.py**: Validation des variables d'environnement

## Base de Données

### Schéma PostgreSQL

#### Table: users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(64),
    last_name VARCHAR(64),
    is_approved BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### Table: roles
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(255),
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: jurisprudence_cases
```sql
CREATE TABLE jurisprudence_cases (
    id SERIAL PRIMARY KEY,
    ref VARCHAR(100) UNIQUE NOT NULL,
    titre VARCHAR(500),
    juridiction VARCHAR(200),
    pays VARCHAR(100),
    ville VARCHAR(100),
    numero_decision VARCHAR(100),
    date_decision DATE,
    numero_dossier VARCHAR(100),
    type_decision VARCHAR(100),
    chambre VARCHAR(100),
    theme VARCHAR(200),
    mots_cles VARCHAR(500),
    base_legale TEXT,
    source VARCHAR(200),
    resume_francais_encrypted TEXT,
    resume_arabe_encrypted TEXT,
    texte_integral_encrypted TEXT,
    pdf_file_path VARCHAR(500),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cases_ref ON jurisprudence_cases(ref);
CREATE INDEX idx_cases_date ON jurisprudence_cases(date_decision);
CREATE INDEX idx_cases_juridiction ON jurisprudence_cases(juridiction);
```

#### Table: search_history
```sql
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    query_encrypted TEXT NOT NULL,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_user_id ON search_history(user_id);
```

### Relations

```
users (1) ──────────> (N) jurisprudence_cases
  │                         (created_by)
  │
  ├─────────────────> (N) search_history
  │                         (user_id)
  │
  └─────────────────> (1) roles
                           (role_id)
```

### Stratégie de Chiffrement

#### Champs Chiffrés (Fernet)
- `resume_francais_encrypted`
- `resume_arabe_encrypted`
- `texte_integral_encrypted`
- `query_encrypted` (dans search_history)

#### Champs Non Chiffrés (pour recherche)
- `ref`, `titre`, `juridiction`
- `date_decision`, `theme`, `mots_cles`
- `base_legale`, `source`

**Raison**: Balance entre sécurité (contenu sensible chiffré) et performance (métadonnées searchables).

## API REST

### Endpoints d'Authentification

#### POST /api/auth/register
Inscription d'un nouvel utilisateur.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "confirmPassword": "SecurePass123",
  "firstName": "Jean",
  "lastName": "Dupont"
}
```

**Response (201):**
```json
{
  "message": "Compte créé avec succès. En attente de validation.",
  "requiresApproval": true
}
```

#### POST /api/auth/login
Connexion utilisateur.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Connexion réussie",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "firstName": "Jean",
    "lastName": "Dupont",
    "isAdmin": false
  }
}
```

#### GET /api/auth/me
Informations utilisateur connecté.

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "firstName": "Jean",
  "lastName": "Dupont",
  "isAdmin": false,
  "isApproved": true
}
```

### Endpoints de Jurisprudence

#### GET /api/cases
Liste paginée des cas.

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20)

**Response (200):**
```json
{
  "cases": [...],
  "total": 2970,
  "page": 1,
  "perPage": 20,
  "totalPages": 149
}
```

#### GET /api/cases/:id
Détails d'un cas spécifique.

**Response (200):**
```json
{
  "id": 1,
  "ref": "CAS-2024-001",
  "titre": "Affaire X vs Y",
  "juridiction": "Cour d'Appel de Casablanca",
  "dateDecision": "2024-01-15",
  "resumeFrancais": "...",
  "resumeArabe": "...",
  "texteIntegral": "...",
  ...
}
```

#### POST /api/search
Recherche IA par description texte.

**Request:**
```json
{
  "query": "Litige commercial sur clause contractuelle abusive"
}
```

**Response (200):**
```json
{
  "success": true,
  "similarCases": [
    {
      "id": 42,
      "ref": "CAS-2023-156",
      "titre": "...",
      "similarity": 0.92
    }
  ],
  "analysis": "Analyse globale de l'IA...",
  "recommendations": "Recommandations juridiques...",
  "totalCasesAnalyzed": 50
}
```

#### POST /api/search-stream
Recherche IA avec streaming SSE.

**Request:**
```json
{
  "query": "..."
}
```

**Response (Server-Sent Events):**
```
data: {"type": "progress", "message": "Indexation..."}
data: {"type": "thinking", "message": "Réflexion en cours..."}
data: {"type": "complete", "result": {...}}
```

### Endpoints d'Import

#### POST /api/batch-import
Import en masse de PDFs (jusqu'à 200).

**Request:** `multipart/form-data`
- `files[]`: array de fichiers PDF

**Response (200):**
```json
{
  "success": true,
  "processed": 150,
  "failed": 0,
  "details": [...]
}
```

### Codes de Statut HTTP

- **200 OK**: Succès
- **201 Created**: Ressource créée
- **400 Bad Request**: Données invalides
- **401 Unauthorized**: Non authentifié
- **403 Forbidden**: Non autorisé
- **404 Not Found**: Ressource introuvable
- **500 Internal Server Error**: Erreur serveur

## Services

### AIService (ai_service.py)

#### Méthode: find_similar_cases()

```python
def find_similar_cases(
    case_description: str,
    existing_cases: list
) -> dict:
    """
    Analyse un cas et trouve des précédents similaires.
    
    Args:
        case_description: Description du cas à analyser
        existing_cases: Liste des cas dans la base
        
    Returns:
        {
            'success': True,
            'similar_cases': [...],
            'analysis': '...',
            'recommendations': '...',
            'similarity_reasons': {...}
        }
    """
```

**Logique:**
1. Indexation des cas (max 50 pour limiter tokens)
2. Construction du prompt bilingue (FR + AR)
3. Requête à OpenRouter API (Claude 3.5 Sonnet)
4. Parsing de la réponse JSON
5. Matching des références avec cas complets
6. Retour des résultats structurés

**Modèle IA:**
- `anthropic/claude-3.5-sonnet`
- Température: 0.3 (précision)
- Max tokens: 3000
- Timeout: 60s

### PDFExtractorService (pdf_extractor.py)

#### Méthode: extract_case_from_pdf()

```python
def extract_case_from_pdf(pdf_path: str) -> dict:
    """
    Extrait les champs structurés d'un PDF juridique.
    
    Args:
        pdf_path: Chemin du fichier PDF
        
    Returns:
        {
            'ref': 'CAS-2024-001',
            'titre': '...',
            'juridiction': '...',
            'resume_francais': '...',
            'resume_arabe': '...',
            ...
        }
    """
```

**Patterns Regex:**
```python
patterns = {
    'ref': r'Ref[:\s]+([^\n]+)',
    'titre': r'Titre[:\s]+([^\n]+)',
    'juridiction': r'Juridiction[:\s]+([^\n]+)',
    'resume_fr': r'Résumé \(en français\)[:\s]+(.*?)(?=Résumé|Texte|$)',
    'resume_ar': r'Résumé \(en arabe\)[:\s]+(.*?)(?=Texte|$)',
    ...
}
```

### EncryptionService (encryption.py)

```python
class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, text: str) -> str:
        """Chiffre un texte et retourne base64."""
        
    def decrypt(self, encrypted_text: str) -> str:
        """Déchiffre un texte base64."""
```

**Sécurité:**
- Algorithme: Fernet (AES-128 CBC + HMAC)
- Clé: 32 bytes générée avec `Fernet.generate_key()`
- Encodage: Base64 pour stockage en DB

## Sécurité

### Authentification

#### Flask-Login
```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentification requise'}), 401
```

#### Protection des Routes
```python
from flask_login import login_required, current_user

@cases_bp.route('/api/cases', methods=['POST'])
@login_required
def create_case():
    if not current_user.is_admin:
        return jsonify({'error': 'Accès refusé'}), 403
    ...
```

### Protection CSRF

```python
csrf = CSRFProtect(app)

# Exemption pour APIs JSON
csrf.exempt(auth_bp)
csrf.exempt(cases_bp)
csrf.exempt(batch_import_bp)
csrf.exempt(roles_bp)
```

**Note:** En production avec frontend séparé, utiliser tokens CSRF dans headers.

### Gestion des Mots de Passe

```python
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Hashage
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# Vérification
if bcrypt.check_password_hash(user.password_hash, password):
    # Connexion OK
```

### CORS Configuration

```python
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
```

**Production:** Limiter aux domaines autorisés uniquement.

### Headers de Sécurité

```python
@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Performance

### Optimisations Base de Données

#### Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_cases_ref ON jurisprudence_cases(ref);
CREATE INDEX idx_cases_date ON jurisprudence_cases(date_decision);
```

#### Pagination
```python
page = request.args.get('page', 1, type=int)
per_page = 20
cases_query = JurisprudenceCase.query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)
```

### Cache HTTP

```python
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

**Raison:** Application hautement dynamique avec données sensibles.

### Gunicorn Workers

```bash
gunicorn --workers 4 \
         --threads 2 \
         --timeout 120 \
         --bind 0.0.0.0:5000 \
         main:app
```

**Formule:** `workers = (2 x CPU_cores) + 1`

## Tests

### Structure de Tests (À Implémenter)

```
tests/
├── __init__.py
├── test_auth.py          # Tests authentification
├── test_cases.py         # Tests gestion cas
├── test_search.py        # Tests recherche IA
├── test_import.py        # Tests import PDF
└── conftest.py           # Fixtures pytest
```

### Exemple de Test Unitaire

```python
import pytest
from backend.app import app, db
from backend.models.user import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'Test123!',
        'confirmPassword': 'Test123!',
        'firstName': 'Test',
        'lastName': 'User'
    })
    assert response.status_code == 201
    assert b'Compte cr' in response.data
```

### Tests d'Intégration

```python
def test_full_search_workflow(client, auth):
    # 1. Login
    auth.login()
    
    # 2. Créer un cas (admin)
    response = client.post('/api/cases', json={...})
    assert response.status_code == 201
    
    # 3. Rechercher
    response = client.post('/api/search', json={
        'query': 'Test case description'
    })
    assert response.status_code == 200
    assert 'similar_cases' in response.json
```

## Monitoring et Logs

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Métriques Recommandées

- Temps de réponse API
- Nombre de requêtes IA par jour
- Taux d'erreur par endpoint
- Utilisation CPU/RAM
- Connexions DB actives

## Maintenance

### Backup Base de Données

```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240101.sql
```

### Migration de Données

Utiliser `migrate_database_safe.py` pour migrations structurelles :

```bash
python migrate_database_safe.py
```

### Rotation Clé de Chiffrement

1. Générer nouvelle clé Fernet
2. Déchiffrer toutes les données avec ancienne clé
3. Rechiffrer avec nouvelle clé
4. Mettre à jour `ENCRYPTION_KEY`

## Support

Pour toute question technique :
- Documentation: README.md
- Déploiement: DEPLOYMENT.md
- Contact: admin système
