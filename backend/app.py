from flask import Flask, render_template, send_from_directory, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from backend.config import Config
from backend.models.user import db, User
from backend.routes.auth import auth_bp, bcrypt
from backend.routes.cases import cases_bp
from backend.routes.batch_import import batch_import_bp

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config.from_object(Config)

CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

csrf = CSRFProtect(app)
csrf.exempt(auth_bp)
csrf.exempt(cases_bp)

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

@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"⚠️  Tables already exist or error creating tables: {e}")
    
    try:
        admin = User.query.filter_by(email='admin@jurisprudence.com').first()
        if not admin:
            from flask_bcrypt import generate_password_hash
            admin_user = User(
                email='admin@jurisprudence.com',
                password_hash=generate_password_hash('Admin123!').decode('utf-8'),
                first_name='Admin',
                last_name='System',
                is_approved=True,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Administrateur créé: admin@jurisprudence.com / Admin123!")
    except Exception as e:
        print(f"⚠️  Error checking/creating admin user: {e}")

