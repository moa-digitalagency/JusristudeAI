from flask import Flask, render_template, send_from_directory, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from backend.config import Config
from backend.models.user import db, User
from backend.routes.auth import auth_bp, bcrypt
from backend.routes.cases import cases_bp
from backend.routes.batch_import import batch_import_bp
from backend.routes.roles import roles_bp
from backend.routes.settings import settings_bp
from backend.utils.secrets_checker import secrets_checker

secrets_checker.check_and_exit_if_missing_critical()

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

csrf = CSRFProtect(app)
csrf.exempt(auth_bp)
csrf.exempt(cases_bp)
csrf.exempt(batch_import_bp)
csrf.exempt(roles_bp)
csrf.exempt(settings_bp)

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentification requise'}), 401

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(cases_bp, url_prefix='/api')
app.register_blueprint(batch_import_bp, url_prefix='/api')
app.register_blueprint(roles_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/api')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/admin')
def admin_page():
    return render_template('admin_new.html')

@app.route('/admin/roles')
def admin_roles_page():
    return render_template('admin_roles.html')

@app.route('/admin/settings')
def admin_settings_page():
    return render_template('admin_settings.html')

@app.route('/cases')
def cases_page():
    return render_template('cases.html')

@app.route('/case/<int:case_id>')
def case_detail_page(case_id):
    return render_template('case_detail.html', case_id=case_id)

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"⚠️  Tables already exist or error creating tables: {e}")
    
    from backend.init_roles import initialize_roles_and_permissions
    try:
        initialize_roles_and_permissions(app)
    except Exception as e:
        print(f"⚠️  Error initializing roles and permissions: {e}")
    
    try:
        from backend.models.settings import Settings
        Settings.initialize_defaults()
        print("✓ Paramètres initialisés")
    except Exception as e:
        print(f"⚠️  Error initializing settings: {e}")
    
    try:
        from backend.models.role import Role
        admin = User.query.filter_by(email='admin@jurisprudence.com').first()
        admin_role = Role.query.filter_by(name='Administrateur').first()
        
        if not admin:
            from flask_bcrypt import generate_password_hash
            admin_user = User(
                email='admin@jurisprudence.com',
                password_hash=generate_password_hash('Admin123!').decode('utf-8'),
                first_name='Admin',
                last_name='System',
                is_approved=True,
                is_admin=True,
                role_id=admin_role.id if admin_role else None
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Administrateur créé: admin@jurisprudence.com / Admin123!")
    except Exception as e:
        print(f"⚠️  Error checking/creating admin user: {e}")

