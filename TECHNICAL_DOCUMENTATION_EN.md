# 📖 Technical Documentation - Legal Case Law AI Database

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Project Structure](#project-structure)
3. [Database](#database)
4. [REST API](#rest-api)
5. [Services](#services)
6. [Security](#security)
7. [Performance](#performance)
8. [Testing](#testing)

## System Architecture

### Overview

The application follows an **MVC (Model-View-Controller)** architecture adapted for Flask:

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
│    Flask    │ ← Web Application
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

### Data Flow

1. **Incoming Request** → Nginx (if configured) → Gunicorn → Flask
2. **Authentication** → Flask-Login verifies session
3. **Authorization** → Decorators check permissions
4. **Processing** → Route calls service if needed
5. **Database** → SQLAlchemy ORM manages queries
6. **Response** → JSON or rendered HTML template

## Project Structure

### Detailed Tree

```
jurisprudence-platform/
│
├── backend/                        # Server code
│   ├── __init__.py
│   ├── app.py                     # Flask entry point
│   ├── config.py                  # Central configuration
│   ├── init_roles.py              # Roles initialization
│   │
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── user.py               # User model + db
│   │   ├── case.py               # JurisprudenceCase model
│   │   └── role.py               # Role + Permission model
│   │
│   ├── routes/                    # API controllers
│   │   ├── __init__.py
│   │   ├── auth.py               # /api/auth/* endpoints
│   │   ├── cases.py              # /api/cases/* endpoints
│   │   ├── batch_import.py       # /api/batch-import/* endpoints
│   │   └── roles.py              # /api/roles/* endpoints
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py         # OpenRouter service
│   │   └── pdf_extractor.py     # PDF extraction service
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── encryption.py         # Fernet encryption
│       ├── text_cleaner.py       # Text cleaning
│       └── secrets_checker.py    # Secrets validation
│
├── frontend/                       # User interface
│   ├── static/
│   │   ├── css/
│   │   │   └── moa-design.css   # Complete design system
│   │   └── js/
│   │       ├── login.js
│   │       ├── register.js
│   │       ├── dashboard.js
│   │       ├── search.js
│   │       ├── cases.js
│   │       ├── admin_new.js
│   │       └── admin_roles.js
│   │
│   └── templates/                 # Jinja2 templates
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── search.html
│       ├── cases.html
│       ├── case_detail.html
│       ├── admin_new.html
│       └── admin_roles.html
│
├── uploads/                        # Uploaded files
│   └── pdfs/                      # Imported PDFs
│       ├── single/                # Single imports
│       └── batch_*/               # Batch imports
│
├── main.py                         # Main entry point
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
├── README_EN.md                    # User documentation
├── TECHNICAL_DOCUMENTATION_EN.md   # This file
└── DEPLOYMENT_EN.md                # Deployment guide
```

### Module Responsibilities

#### backend/app.py
- Flask application initialization
- Extension configuration (CORS, CSRF, Login)
- Blueprint registration
- HTTP cache management
- Template rendering routes
- Automatic database creation
- System roles initialization
- Default admin account creation

#### backend/config.py
```python
class Config:
    SECRET_KEY: str                 # Flask session key
    DATABASE_URL: str               # PostgreSQL URL
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    ENCRYPTION_KEY: bytes           # Fernet key
    OPENROUTER_API_KEY: str         # OpenRouter API key
    OPENROUTER_API_URL: str         # OpenRouter API URL
```

## Database

### PostgreSQL Schema

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

### Encryption Strategy

#### Encrypted Fields (Fernet)
- `resume_francais_encrypted`
- `resume_arabe_encrypted`
- `texte_integral_encrypted`
- `query_encrypted` (in search_history)

#### Non-Encrypted Fields (for search)
- `ref`, `titre`, `juridiction`
- `date_decision`, `theme`, `mots_cles`
- `base_legale`, `source`

**Reason**: Balance between security (sensitive content encrypted) and performance (searchable metadata).

## REST API

### Authentication Endpoints

#### POST /api/auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "confirmPassword": "SecurePass123",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response (201):**
```json
{
  "message": "Account created successfully. Pending approval.",
  "requiresApproval": true
}
```

#### POST /api/auth/login
User login.

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
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "isAdmin": false
  }
}
```

### Case Law Endpoints

#### GET /api/cases
Paginated list of cases.

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

#### POST /api/search
AI search by text description.

**Request:**
```json
{
  "query": "Commercial dispute on abusive contractual clause"
}
```

**Response (200):**
```json
{
  "success": true,
  "similarCases": [...],
  "analysis": "AI global analysis...",
  "recommendations": "Legal recommendations...",
  "totalCasesAnalyzed": 50
}
```

## Services

### AIService (ai_service.py)

#### Method: find_similar_cases()

```python
def find_similar_cases(
    case_description: str,
    existing_cases: list
) -> dict:
    """
    Analyze a case and find similar precedents.
    
    Args:
        case_description: Case description to analyze
        existing_cases: List of cases in database
        
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

**Logic:**
1. Case indexing (max 50 to limit tokens)
2. Bilingual prompt construction (FR + AR)
3. OpenRouter API request (Claude 3.5 Sonnet)
4. JSON response parsing
5. Reference matching with complete cases
6. Structured results return

**AI Model:**
- `anthropic/claude-3.5-sonnet`
- Temperature: 0.3 (precision)
- Max tokens: 3000
- Timeout: 60s

### PDFExtractorService (pdf_extractor.py)

#### Method: extract_case_from_pdf()

```python
def extract_case_from_pdf(pdf_path: str) -> dict:
    """
    Extract structured fields from a legal PDF.
    
    Args:
        pdf_path: PDF file path
        
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

## Security

### Authentication

#### Flask-Login
```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentication required'}), 401
```

#### Route Protection
```python
from flask_login import login_required, current_user

@cases_bp.route('/api/cases', methods=['POST'])
@login_required
def create_case():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    ...
```

### Password Management

```python
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Hashing
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# Verification
if bcrypt.check_password_hash(user.password_hash, password):
    # Login OK
```

### Encryption Service

```python
class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, text: str) -> str:
        """Encrypt text and return base64."""
        
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt base64 text."""
```

**Security:**
- Algorithm: Fernet (AES-128 CBC + HMAC)
- Key: 32 bytes generated with `Fernet.generate_key()`
- Encoding: Base64 for DB storage

## Performance

### Database Optimizations

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

### Gunicorn Workers

```bash
gunicorn --workers 4 \
         --threads 2 \
         --timeout 120 \
         --bind 0.0.0.0:5000 \
         main:app
```

**Formula:** `workers = (2 x CPU_cores) + 1`

## Testing

### Test Structure (To Implement)

```
tests/
├── __init__.py
├── test_auth.py          # Authentication tests
├── test_cases.py         # Case management tests
├── test_search.py        # AI search tests
├── test_import.py        # PDF import tests
└── conftest.py           # pytest fixtures
```

### Unit Test Example

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
```

## Monitoring and Logs

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

### Recommended Metrics

- API response time
- AI requests per day
- Error rate per endpoint
- CPU/RAM usage
- Active DB connections

## Maintenance

### Database Backup

```bash
# Backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240101.sql
```

### Data Migration

Use `migrate_database_safe.py` for structural migrations:

```bash
python migrate_database_safe.py
```

## Support

For technical questions:
- Documentation: README_EN.md
- Deployment: DEPLOYMENT_EN.md
- Contact: system administrator
