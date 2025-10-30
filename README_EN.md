# 📚 Legal Case Law Database - AI-Powered Legal Research Platform

## 📋 Description

Professional web application for managing and intelligently searching Moroccan case law, powered by artificial intelligence. The platform enables legal professionals to efficiently search for legal precedents, manage a secure case database, and obtain AI analysis for their litigation.

## ✨ Key Features

### 🔐 Authentication and Security

#### Complete Authentication System
- **Secure Registration** with password validation (8+ characters minimum)
- **Email/Password Login** with Flask-Login sessions
- **Administrator Validation**: new users pending approval
- **Test Account Provided**: admin@jurisprudence.com / Admin123!
- **CSRF Protection** integrated on all routes
- **Role Management**: User, Manager, Administrator

#### Data Security
- **Fernet Encryption** for all sensitive legal data (summaries, full texts)
- **Bcrypt Hashing** for all passwords
- **SQL Injection Prevention** via SQLAlchemy ORM
- **Encryption Keys** managed via secure environment variables
- **Secure Sessions** with HTTPOnly cookies

### 📊 Case Law Management

#### Robust Database
- **PostgreSQL** for robustness and scalability
- **2970+ cases** of Moroccan case law stored
- **Bilingual Support**: French and Arabic
- **20+ fields** per case: reference, title, jurisdiction, dates, themes, etc.
- **Automatic Encryption** of sensitive data
- **Optimized Indexes** for fast searches

#### Visualization and Navigation
- **Paginated List** of all cases (20 per page)
- **Dashboard** with the 5 most recent cases
- **Detailed Page** for each case with all information
- **Colored Badges** for categories and statuses
- **Complete Metadata**: court, date, decision type, chamber

#### Administrative Management (Full CRUD)
- **Case Creation** via complete form
- **Modification** of existing cases with edit modal
- **Deletion** of cases with confirmation
- **Bulk Import**: CSV, Excel, PDF (up to 200 files)
- **Automatic Validation** of imported data
- **Traceability**: recording of creating user

### 🤖 AI-Powered Search

#### Advanced AI Analysis
- **OpenRouter API Integration** with Claude 3.5 Sonnet
- **Contextual Analysis** of cases with legal similarity
- **Recommendations** for litigation based on precedents
- **Bilingual Support**: analysis in French AND Arabic
- **Real-time Streaming**: progressive analysis display
- **Encrypted History** of all searches

#### Dual Search Mode
- **Text Mode**: textual case description
- **Document Mode**: PDF or Word upload (.docx)
- **Automatic Extraction** of text from documents
- **Same Precision** of analysis for both modes
- **Tabbed Interface** to easily switch

#### Search Results
- **List of Similar Cases** with relevance scores
- **Detailed Reasons** for similarity for each case
- **Global Analysis** of applicable case law
- **Strategic Recommendations** for defense
- **Formatted Display** with badges and colored sections

### 📥 Document Import and Extraction

#### Bulk PDF Import
- **Batch Import**: up to 200 PDFs simultaneously
- **Automatic Extraction** of all structured fields
- **Moroccan Format Support**: recognition of specific patterns
- **Real-time Progress Bar**
- **Error Handling**: detailed failure report
- **Duplicate Prevention**: reference verification

#### Simple PDF Import
- **Single Upload** with immediate extraction
- **Preview** of extracted data
- **Manual Confirmation** before saving
- **Automatically Extracted Fields**:
  - Reference (mandatory)
  - Title and jurisdiction
  - Dates and decision numbers
  - Theme and keywords
  - Encrypted summaries (FR/AR)
  - Encrypted full text

### 👨‍💼 Administration Panel

#### User Management
- **Full CRUD**: create, read, update, delete
- **Advanced Filtering**: all / pending / approved
- **Bulk Actions**: approval/suspension/deletion
- **Protection**: impossible to modify own account
- **Detailed Information**: name, email, role, registration date
- **Status Badges**: Pending, Approved, Administrator

#### Roles and Permissions Management
- **Custom Role Creation**
- **Granular Permission Assignment**
- **Modification** of existing roles
- **Secure Deletion** with checks
- **Dedicated Page**: /admin/roles

#### Statistics and Metrics
- **Total Number of Cases** in database
- **Search Counter** per user
- **Recent Cases** on dashboard
- **Real-time Updates**

### 🎨 User Interface and Design

#### MOA Design System
- **Colored Dotted Borders** (3px dotted) - visual signature
- **Professional Palette**: blue, green, purple, cyan, pink, yellow
- **Colored Sections** by category with hover effects
- **Colored Badges** for quick identification
- **Buttons** with shadows and smooth animations
- **Optimized Typography**: 0.95rem base, clear hierarchy

#### Navigation and Pages
- **Responsive Navbar** with logo and contextual links
- **Login**: login page with test account
- **Register**: registration with validation
- **Dashboard**: overview with statistics
- **Search**: AI search with dual mode
- **Cases**: paginated case law list
- **Case Detail**: complete case details
- **Admin**: complete tabbed interface
- **Admin Roles**: role and permission management

#### Mobile Responsive Design
- **Mobile-first**: optimized for all screens
- **Media Queries**: breakpoints at 768px and 480px
- **Adaptive Grids**: 1 column on mobile, 2-3 on desktop
- **Stacked Navigation** vertically on mobile
- **Adjusted Sizes**: reduced fonts and padding
- **Full-width Buttons** on small screen

## 🚀 Installation and Configuration

### Prerequisites
- Python 3.11+
- PostgreSQL
- OpenRouter Account (for AI)

### Installation

1. **Clone the project**
```bash
git clone <repo-url>
cd jurisprudence-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Required secrets:
- `DATABASE_URL`: PostgreSQL URL
- `SESSION_SECRET`: Flask secret key
- `ENCRYPTION_KEY`: Fernet key
- `OPENROUTER_API_KEY`: OpenRouter API key

**Generate encryption key:**
```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

4. **Initialize database**

Tables are created automatically on startup. A default admin account is created:
- Email: `admin@jurisprudence.com`
- Password: `Admin123!`

5. **Launch application**
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

Application accessible at `http://0.0.0.0:5000`

## 🔧 Technology Stack

### Backend
- **Flask 3.1.2**: Python web framework
- **SQLAlchemy 2.0.44**: PostgreSQL ORM
- **Flask-Login 0.6.3**: session management
- **Flask-Bcrypt 1.0.1**: password hashing
- **Cryptography 46.0.3**: Fernet encryption
- **Gunicorn 23.0.0**: production WSGI server

### Document Processing
- **PyPDF2 3.0.1**: PDF text extraction
- **python-docx 1.2.0**: Word file reading
- **openpyxl 3.1.5**: Excel import/export
- **pandas 2.3.3**: data manipulation

### Database
- **PostgreSQL**: relational database
- **psycopg2-binary 2.9.11**: PostgreSQL adapter

### Frontend
- **Vanilla JavaScript**: no heavy framework
- **Custom CSS**: MOA Design System
- **Server-Sent Events (SSE)**: real-time streaming

## 📊 Data Model

### User
```python
id, email, password_hash
first_name, last_name
is_approved, is_admin
role_id, created_at
```

### JurisprudenceCase
```python
id, ref, titre, juridiction
pays, ville, numero_decision
date_decision, type_decision
chambre, theme, mots_cles
base_legale, source
resume_francais_encrypted
resume_arabe_encrypted
texte_integral_encrypted
created_by, created_at
```

### Role
```python
id, name, description
permissions (JSON)
created_at
```

### SearchHistory
```python
id, user_id
query_encrypted
results_count, created_at
```

## 🔒 Security and Privacy

### Data Encryption
- **Algorithm**: Fernet (AES 128-bit CBC mode)
- **Encrypted Data**:
  - Case summaries (French and Arabic)
  - Full text of decisions
  - User search history
- **Encryption Key**: stored in secure secrets
- **Rotation**: migration possible with new key

### Authentication
- **Hashing**: bcrypt with automatic salt
- **Sessions**: Flask-Login with secure cookies
- **Validation**: unique email, strong password (8+ characters)
- **Approval**: administrator validates new accounts
- **CSRF Protection**: token on all POST/PUT/DELETE requests

## 📱 Mobile Compatibility

The application is **100% responsive** and optimized for:

- **Smartphones**: iPhone, Android (320px - 767px)
- **Tablets**: iPad, Android tablets (768px - 1023px)
- **Desktop**: all screens (1024px+)

### CSS Breakpoints
- **480px**: full-width buttons, stacked navigation
- **768px**: 1 column grids, reduced fonts, adjusted padding

## 📄 Additional Documentation

- **[TECHNICAL_DOCUMENTATION_EN.md](TECHNICAL_DOCUMENTATION_EN.md)**: Complete technical architecture
- **[DEPLOYMENT_EN.md](DEPLOYMENT_EN.md)**: Production deployment guide

## 🐛 Support and Contribution

### Report a Bug

Create an issue with:
1. Problem description
2. Steps to reproduce
3. Expected vs observed behavior
4. Screenshots if applicable

### Contribute

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

© 2024-2025 - Legal Case Law AI Database
Developed with the MOA Design System

---

**Note**: This application is designed for the Moroccan legal system but can be adapted to other jurisdictions.

For any questions: contact the system administrator.
