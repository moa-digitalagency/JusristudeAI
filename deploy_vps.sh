#!/bin/bash

###############################################################################
# Jurisprudence AI Platform - VPS Deployment Script
# 
# This script automates the deployment of the Jurisprudence AI platform
# on an Ubuntu 20.04/22.04 VPS.
#
# Usage:
#   sudo ./deploy_vps.sh
#
# Prerequisites:
#   - Ubuntu 20.04 LTS or 22.04 LTS
#   - Root or sudo access
#   - Git installed
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
APP_NAME="jurisprudence"
APP_DIR="/var/www/jurisprudence-platform"
APP_USER="www-data"
DOMAIN=""
DB_NAME="jurisprudence_db"
DB_USER="jurisprudence"
DB_PASS=""
SESSION_SECRET=""
ENCRYPTION_KEY=""
OPENROUTER_API_KEY=""

###############################################################################
# Helper Functions
###############################################################################

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_section() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run this script as root or with sudo"
        exit 1
    fi
}

generate_random_string() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-${1:-32}
}

###############################################################################
# Configuration Input
###############################################################################

collect_configuration() {
    print_section "Configuration"
    
    # Domain name
    read -p "Enter your domain name (e.g., jurisprudence.example.com): " DOMAIN
    if [ -z "$DOMAIN" ]; then
        print_error "Domain name is required"
        exit 1
    fi
    
    # Database password
    read -sp "Enter PostgreSQL password for user '$DB_USER' (or press Enter for auto-generate): " DB_PASS_INPUT
    echo
    if [ -z "$DB_PASS_INPUT" ]; then
        DB_PASS=$(generate_random_string 32)
        print_info "Generated database password: $DB_PASS"
    else
        DB_PASS="$DB_PASS_INPUT"
    fi
    
    # OpenRouter API Key
    read -p "Enter your OpenRouter API Key: " OPENROUTER_API_KEY
    if [ -z "$OPENROUTER_API_KEY" ]; then
        print_warning "OpenRouter API key not provided. AI search will not work."
        read -p "Continue anyway? (y/N): " continue_without_api
        if [[ ! "$continue_without_api" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Generate encryption key
    print_info "Generating encryption key..."
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "")
    
    if [ -z "$ENCRYPTION_KEY" ]; then
        print_warning "Failed to generate encryption key. Installing cryptography..."
        pip3 install cryptography
        ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    fi
    
    # Generate session secret
    SESSION_SECRET=$(generate_random_string 64)
    
    print_success "Configuration collected"
}

###############################################################################
# System Update
###############################################################################

update_system() {
    print_section "Updating System"
    
    apt update
    apt upgrade -y
    apt install -y software-properties-common curl wget git build-essential
    
    print_success "System updated"
}

###############################################################################
# Python Installation
###############################################################################

install_python() {
    print_section "Installing Python 3.11"
    
    if command -v python3.11 &> /dev/null; then
        print_info "Python 3.11 already installed"
    else
        add-apt-repository ppa:deadsnakes/ppa -y
        apt update
        apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    fi
    
    python3.11 --version
    print_success "Python 3.11 installed"
}

###############################################################################
# PostgreSQL Installation
###############################################################################

install_postgresql() {
    print_section "Installing PostgreSQL"
    
    apt install -y postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    print_info "Creating database and user..."
    
    sudo -u postgres psql <<EOF
-- Drop if exists
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Exit
\q
EOF
    
    print_success "PostgreSQL installed and configured"
}

###############################################################################
# Nginx Installation
###############################################################################

install_nginx() {
    print_section "Installing Nginx"
    
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Allow HTTP and HTTPS through firewall
    ufw allow 'Nginx Full'
    
    print_success "Nginx installed"
}

###############################################################################
# Application Setup
###############################################################################

setup_application() {
    print_section "Setting up Application"
    
    # Create directory
    mkdir -p /var/www
    
    # Clone repository (you'll need to update this URL)
    if [ -d "$APP_DIR" ]; then
        print_warning "Directory $APP_DIR already exists. Pulling latest changes..."
        cd $APP_DIR
        git pull
    else
        print_info "Cloning repository..."
        read -p "Enter Git repository URL: " REPO_URL
        if [ -z "$REPO_URL" ]; then
            print_error "Repository URL is required"
            exit 1
        fi
        git clone "$REPO_URL" $APP_DIR
    fi
    
    cd $APP_DIR
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    print_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create uploads directory
    mkdir -p uploads/pdfs/single
    mkdir -p uploads/pdfs/batch
    
    # Set permissions
    chown -R $APP_USER:$APP_USER $APP_DIR
    chmod -R 755 $APP_DIR
    
    print_success "Application setup complete"
}

###############################################################################
# Environment Configuration
###############################################################################

configure_environment() {
    print_section "Configuring Environment"
    
    # Create environment file
    cat > $APP_DIR/.env <<EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME
SESSION_SECRET=$SESSION_SECRET
ENCRYPTION_KEY=$ENCRYPTION_KEY
OPENROUTER_API_KEY=$OPENROUTER_API_KEY
FLASK_ENV=production
DEBUG=False
EOF
    
    chmod 600 $APP_DIR/.env
    chown $APP_USER:$APP_USER $APP_DIR/.env
    
    print_success "Environment configured"
}

###############################################################################
# Database Initialization
###############################################################################

initialize_database() {
    print_section "Initializing Database"
    
    cd $APP_DIR
    source venv/bin/activate
    
    # Source environment
    export $(cat .env | xargs)
    
    # Initialize database
    python3 -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
    
    print_success "Database initialized"
}

###############################################################################
# Gunicorn Service
###############################################################################

setup_gunicorn_service() {
    print_section "Setting up Gunicorn Service"
    
    # Create log directory
    mkdir -p /var/log/gunicorn
    chown $APP_USER:$APP_USER /var/log/gunicorn
    
    # Create systemd service
    cat > /etc/systemd/system/$APP_NAME.service <<EOF
[Unit]
Description=Jurisprudence AI Gunicorn Service
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
RuntimeDirectory=gunicorn
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn \\
          --workers 4 \\
          --threads 2 \\
          --timeout 120 \\
          --bind unix:/run/gunicorn/$APP_NAME.sock \\
          --access-logfile /var/log/gunicorn/access.log \\
          --error-logfile /var/log/gunicorn/error.log \\
          main:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd, enable and start service
    systemctl daemon-reload
    systemctl enable $APP_NAME
    systemctl start $APP_NAME
    
    # Check status
    sleep 2
    if systemctl is-active --quiet $APP_NAME; then
        print_success "Gunicorn service started successfully"
    else
        print_error "Gunicorn service failed to start. Check logs: journalctl -u $APP_NAME"
        exit 1
    fi
}

###############################################################################
# Nginx Configuration
###############################################################################

configure_nginx() {
    print_section "Configuring Nginx"
    
    # Create Nginx configuration
    cat > /etc/nginx/sites-available/$APP_NAME <<EOF
upstream ${APP_NAME}_app {
    server unix:/run/gunicorn/$APP_NAME.sock fail_timeout=0;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        proxy_pass http://${APP_NAME}_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias $APP_DIR/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias $APP_DIR/uploads/;
        internal;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Restart Nginx
    systemctl restart nginx
    
    print_success "Nginx configured"
}

###############################################################################
# SSL Configuration
###############################################################################

configure_ssl() {
    print_section "Configuring SSL (Let's Encrypt)"
    
    read -p "Do you want to configure SSL with Let's Encrypt? (y/N): " configure_ssl_input
    
    if [[ "$configure_ssl_input" =~ ^[Yy]$ ]]; then
        # Install Certbot
        apt install -y certbot python3-certbot-nginx
        
        # Obtain certificate
        certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
        
        # Test auto-renewal
        certbot renew --dry-run
        
        print_success "SSL configured"
    else
        print_warning "Skipping SSL configuration. You can configure it later with: certbot --nginx -d $DOMAIN"
    fi
}

###############################################################################
# Firewall Configuration
###############################################################################

configure_firewall() {
    print_section "Configuring Firewall"
    
    # Install UFW if not installed
    apt install -y ufw
    
    # Configure firewall
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    
    # Enable firewall
    echo "y" | ufw enable
    
    ufw status
    
    print_success "Firewall configured"
}

###############################################################################
# Backup Configuration
###############################################################################

setup_backups() {
    print_section "Setting up Automatic Backups"
    
    # Create backup script
    cat > /usr/local/bin/backup-$APP_NAME.sh <<'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/jurisprudence"
DB_NAME="jurisprudence_db"
APP_DIR="/var/www/jurisprudence-platform"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Uploaded files backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz $APP_DIR/uploads/

# Keep only last 30 backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x /usr/local/bin/backup-$APP_NAME.sh
    
    # Add to crontab (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-$APP_NAME.sh >> /var/log/backup-$APP_NAME.log 2>&1") | crontab -
    
    print_success "Automatic backups configured (daily at 2 AM)"
}

###############################################################################
# Final Steps
###############################################################################

display_summary() {
    print_section "Deployment Complete!"
    
    echo -e "${GREEN}Application URL:${NC} http://$DOMAIN"
    echo -e "${GREEN}Admin Email:${NC} admin@jurisprudence.com"
    echo -e "${GREEN}Admin Password:${NC} Admin123! ${YELLOW}(CHANGE THIS IMMEDIATELY!)${NC}"
    echo ""
    echo -e "${BLUE}Database Details:${NC}"
    echo -e "  Name: $DB_NAME"
    echo -e "  User: $DB_USER"
    echo -e "  Password: $DB_PASS"
    echo ""
    echo -e "${BLUE}Important Files:${NC}"
    echo -e "  App Directory: $APP_DIR"
    echo -e "  Environment File: $APP_DIR/.env"
    echo -e "  Nginx Config: /etc/nginx/sites-available/$APP_NAME"
    echo -e "  Systemd Service: /etc/systemd/system/$APP_NAME.service"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  View app logs: ${YELLOW}sudo journalctl -u $APP_NAME -f${NC}"
    echo -e "  Restart app: ${YELLOW}sudo systemctl restart $APP_NAME${NC}"
    echo -e "  View Nginx logs: ${YELLOW}sudo tail -f /var/log/nginx/error.log${NC}"
    echo -e "  Run backup: ${YELLOW}sudo /usr/local/bin/backup-$APP_NAME.sh${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo -e "  1. Change the default admin password"
    echo -e "  2. Test the application at http://$DOMAIN"
    echo -e "  3. Configure SSL if you skipped it (certbot --nginx -d $DOMAIN)"
    echo -e "  4. Test AI search functionality"
    echo -e "  5. Set up monitoring and alerts"
    echo ""
    
    # Save credentials to file
    cat > /root/jurisprudence-credentials.txt <<EOF
Jurisprudence AI Platform - Deployment Credentials
==================================================

Application URL: http://$DOMAIN
Admin Email: admin@jurisprudence.com
Admin Password: Admin123! (CHANGE THIS!)

Database:
  Name: $DB_NAME
  User: $DB_USER
  Password: $DB_PASS

Environment Variables:
  SESSION_SECRET: $SESSION_SECRET
  ENCRYPTION_KEY: $ENCRYPTION_KEY
  OPENROUTER_API_KEY: $OPENROUTER_API_KEY

Generated: $(date)
EOF
    
    chmod 600 /root/jurisprudence-credentials.txt
    
    print_success "Credentials saved to /root/jurisprudence-credentials.txt"
}

###############################################################################
# Main Execution
###############################################################################

main() {
    check_root
    
    print_section "Jurisprudence AI Platform - VPS Deployment"
    print_info "This script will install and configure the application on this server."
    echo ""
    
    read -p "Do you want to continue? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    collect_configuration
    update_system
    install_python
    install_postgresql
    install_nginx
    setup_application
    configure_environment
    initialize_database
    setup_gunicorn_service
    configure_nginx
    configure_ssl
    configure_firewall
    setup_backups
    display_summary
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"
