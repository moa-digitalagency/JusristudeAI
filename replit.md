# Plateforme de Jurisprudence IA

## Overview

A professional legal research platform that enables lawyers and legal professionals to search for case law (jurisprudence) using artificial intelligence. The application leverages OpenRouter's AI API to analyze legal cases and find similar precedents, helping legal professionals build stronger arguments and identify relevant case law.

The platform features secure authentication, encrypted data storage, role-based access control, and an intelligent search system that can analyze case descriptions and recommend similar cases from a PostgreSQL database containing thousands of legal precedents.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: HTML5, CSS3, Vanilla JavaScript
- **Design System**: Custom MOA Design System with dotted borders, colored sections, and responsive layouts
- **Key Features**: 
  - No external CSS frameworks (custom design system)
  - Color-coded sections (blue, green, violet, red) for visual organization
  - Responsive mobile-friendly layouts
  - Badge and button components with hover effects
- **Pages**: Login, Registration, Dashboard, AI Search, Administration
- **Client-Side Logic**: Form validation, API calls with fetch(), session management

### Backend Architecture

**Framework**: Flask (Python 3.11+)
- **Application Structure**: Blueprint-based modular architecture
  - `auth_bp`: Authentication routes (login, register, logout, user info)
  - `cases_bp`: Case management routes (CRUD operations, search, stats)
- **Session Management**: Flask-Login for user session handling
- **Security Features**:
  - CSRF protection via Flask-WTF
  - CORS enabled for localhost origins
  - Bcrypt password hashing
  - Fernet symmetric encryption for sensitive legal data

**Design Pattern**: Service-oriented architecture
- **Services Layer**:
  - `AIService`: Handles OpenRouter API integration for case similarity analysis
  - `EncryptionService`: Manages Fernet encryption/decryption of legal data
- **Models Layer**: SQLAlchemy ORM models
  - `User`: Authentication and user management
  - `JurisprudenceCase`: Legal case storage with encrypted fields
  - `SearchHistory`: User search tracking with encrypted queries

**Key Architectural Decisions**:
1. **Encryption-First Approach**: All sensitive legal data (case descriptions, facts, decisions, search queries) are encrypted at rest using Fernet symmetric encryption
   - Rationale: Legal data is highly sensitive and requires protection
   - Trade-off: Performance overhead for encryption/decryption operations
   
2. **Role-Based Access Control**: Two-tier user system (regular users, administrators)
   - Users: Can search and view cases
   - Administrators: Can approve users, add cases, access admin panel
   - Rationale: Ensures data integrity and controlled access to legal database
   
3. **Admin Approval Workflow**: New user registrations require administrator validation
   - Rationale: Maintains platform quality and prevents unauthorized access
   - Default admin account provided for testing

### Data Storage

**Database**: PostgreSQL
- **Schema Design**:
  - `users` table: id, email (unique/indexed), password_hash, first_name, last_name, is_approved, is_admin, created_at
  - `jurisprudence_cases` table: id, case_number (unique/indexed), title, description_encrypted, facts_encrypted, decision_encrypted, court, date_decision, category, keywords, created_at, created_by (foreign key to users)
  - `search_history` table: id, user_id (foreign key), query_encrypted, results_count, created_at

**Encryption Strategy**:
- Encrypted fields: descriptions, facts, decisions, search queries
- Unencrypted fields: case numbers, titles, courts, dates, categories (for efficient searching/filtering)
- Rationale: Balance between security and search performance

**Indexing**: 
- User email for fast authentication lookups
- Case numbers for quick case retrieval
- Optimized for read-heavy workloads (legal research use case)

### Authentication & Authorization

**Authentication Flow**:
1. User registers → stored with `is_approved=False`
2. Admin approves user → sets `is_approved=True`
3. User can login → Flask-Login session created
4. Protected routes check `@login_required` decorator

**Password Security**:
- Bcrypt hashing with automatic salting
- Minimum 8 character password requirement
- No plain-text password storage

**Session Security**:
- Flask-Login handles session management
- SECRET_KEY for session encryption
- HTTP-only session cookies (implicit with Flask)

## External Dependencies

### Third-Party APIs

**OpenRouter API** (https://openrouter.ai/api/v1/chat/completions)
- **Purpose**: AI-powered case similarity analysis
- **Model Used**: `anthropic/claude-3.5-sonnet`
- **Authentication**: API key via `OPENROUTER_API_KEY` environment variable
- **Usage**: Analyzes case descriptions to find similar precedents from existing case database
- **Rate Limiting**: Subject to OpenRouter's API limits
- **Error Handling**: Graceful degradation if API unavailable (returns error message, doesn't break application)

### Databases

**PostgreSQL**
- **Connection**: Via `DATABASE_URL` environment variable
- **ORM**: SQLAlchemy for database abstraction
- **Purpose**: Primary data store for users, cases, and search history
- **Features Used**: Foreign keys, indexes, ACID transactions

### Python Libraries

**Core Dependencies**:
- `Flask`: Web framework
- `Flask-Login`: User session management
- `Flask-Bcrypt`: Password hashing
- `Flask-SQLAlchemy`: Database ORM
- `Flask-CORS`: Cross-origin resource sharing
- `Flask-WTF`: CSRF protection
- `cryptography` (Fernet): Symmetric encryption
- `requests`: HTTP client for OpenRouter API

**Optional Dependencies** (imported but may not be fully implemented):
- `pandas`: Data manipulation (for potential export features)
- `PyPDF2`: PDF processing (for potential document upload)
- `python-docx`: Word document processing (for potential document upload)

### Environment Variables

**Required**:
- `DATABASE_URL`: PostgreSQL connection string
- `ENCRYPTION_KEY`: Fernet encryption key (generate with `Fernet.generate_key()`)
- `OPENROUTER_API_KEY`: API key for AI service

**Optional**:
- `SECRET_KEY`: Flask session secret (auto-generated if missing, but should be set for production)

**Security Note**: Application generates temporary keys if environment variables missing, but warns user and data will be lost on restart

### Deployment Considerations

**WSGI Server**: Gunicorn recommended for production
**HTTPS**: Strongly recommended for production deployment
**Session Storage**: Currently in-memory; consider Redis for production scaling
**File Storage**: No file upload currently implemented, but imports suggest future feature