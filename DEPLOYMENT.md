# 🚀 Guide de Déploiement - Base de Jurisprudence IA

## Table des Matières

1. [Déploiement Replit](#déploiement-replit)
2. [Déploiement VPS](#déploiement-vps)
3. [Configuration Production](#configuration-production)
4. [Sécurité](#sécurité)
5. [Maintenance](#maintenance)
6. [Troubleshooting](#troubleshooting)

## Déploiement Replit

### Configuration Automatique

L'application est prête pour le déploiement Replit.

#### Étape 1: Variables d'Environnement

Configurez les secrets Replit suivants :

1. **ENCRYPTION_KEY** (Obligatoire)
```bash
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

2. **OPENROUTER_API_KEY** (Obligatoire)
- Obtenez-la sur https://openrouter.ai/
- Section "Keys" → "Create Key"

3. **SESSION_SECRET** (Auto-généré par Replit)

4. **DATABASE_URL** (Auto-généré par Replit)

#### Étape 2: Publier

1. Cliquez sur le bouton **"Deploy"** dans Replit
2. Sélectionnez le mode de déploiement :
   - **Autoscale** : Recommandé (économique, scale automatiquement)
   - **Reserved VM** : Si besoin de toujours tourner
3. Configurez le domaine personnalisé (optionnel)
4. Cliquez sur **"Deploy"**

#### Configuration de Déploiement Replit

Le fichier `.replit` est déjà configuré :

```toml
[deployment]
run = ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
deploymentTarget = "autoscale"
```

### Coûts Replit

- **Autoscale** : ~$0.50-2/mois (selon trafic)
- **Reserved VM** : ~$7-20/mois (toujours actif)
- **Base de données** : Incluse

## Déploiement VPS

### Prérequis Serveur

- **OS** : Ubuntu 20.04 LTS ou 22.04 LTS
- **RAM** : Minimum 2 GB (4 GB recommandé)
- **CPU** : Minimum 1 vCPU (2 vCPU recommandé)
- **Stockage** : Minimum 20 GB
- **Accès** : SSH avec sudo

### Installation Rapide (Script Automatique)

```bash
# Télécharger le script de déploiement
wget https://your-repo/deploy_vps.sh

# Rendre exécutable
chmod +x deploy_vps.sh

# Exécuter (en tant que root ou avec sudo)
sudo ./deploy_vps.sh
```

Le script installe automatiquement :
- Python 3.11
- PostgreSQL 14
- Nginx
- Gunicorn
- Certbot (SSL Let's Encrypt)

### Installation Manuelle

#### 1. Mise à Jour Système

```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Installer Python 3.11

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
```

#### 3. Installer PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib

# Créer utilisateur et base de données
sudo -u postgres psql
```

```sql
CREATE USER jurisprudence WITH PASSWORD 'votre_mot_de_passe_securise';
CREATE DATABASE jurisprudence_db OWNER jurisprudence;
GRANT ALL PRIVILEGES ON DATABASE jurisprudence_db TO jurisprudence;
\q
```

#### 4. Installer Nginx

```bash
sudo apt install -y nginx
```

#### 5. Cloner le Projet

```bash
cd /var/www
sudo git clone https://github.com/votre-username/jurisprudence-platform.git
cd jurisprudence-platform
```

#### 6. Créer l'Environnement Virtuel

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 7. Configurer les Variables d'Environnement

```bash
sudo nano /etc/environment
```

Ajouter :
```
DATABASE_URL="postgresql://jurisprudence:votre_mot_de_passe@localhost/jurisprudence_db"
SESSION_SECRET="votre_clé_secrète_aléatoire_32_caractères"
ENCRYPTION_KEY="votre_clé_fernet_générée"
OPENROUTER_API_KEY="votre_clé_openrouter"
```

Recharger :
```bash
source /etc/environment
```

#### 8. Initialiser la Base de Données

```bash
python -c "from backend.app import app, db; app.app_context().push(); db.create_all()"
```

#### 9. Configurer Gunicorn (Systemd Service)

```bash
sudo nano /etc/systemd/system/jurisprudence.service
```

Contenu :
```ini
[Unit]
Description=Jurisprudence IA Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/jurisprudence-platform
Environment="PATH=/var/www/jurisprudence-platform/venv/bin"
Environment="DATABASE_URL=postgresql://jurisprudence:PASSWORD@localhost/jurisprudence_db"
Environment="SESSION_SECRET=YOUR_SESSION_SECRET"
Environment="ENCRYPTION_KEY=YOUR_ENCRYPTION_KEY"
Environment="OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY"
ExecStart=/var/www/jurisprudence-platform/venv/bin/gunicorn \
          --workers 4 \
          --threads 2 \
          --timeout 120 \
          --bind unix:/run/gunicorn/jurisprudence.sock \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          main:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Créer les répertoires de logs :
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

Activer et démarrer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable jurisprudence
sudo systemctl start jurisprudence
sudo systemctl status jurisprudence
```

#### 10. Configurer Nginx

```bash
sudo nano /etc/nginx/sites-available/jurisprudence
```

Contenu :
```nginx
upstream jurisprudence_app {
    server unix:/run/gunicorn/jurisprudence.sock fail_timeout=0;
}

server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://jurisprudence_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static/ {
        alias /var/www/jurisprudence-platform/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /var/www/jurisprudence-platform/uploads/;
        internal;
    }
}
```

Activer le site :
```bash
sudo ln -s /etc/nginx/sites-available/jurisprudence /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 11. Configurer SSL avec Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com
```

Renouvellement automatique :
```bash
sudo certbot renew --dry-run
```

## Configuration Production

### Variables d'Environnement de Production

```bash
# Base de données
DATABASE_URL="postgresql://user:pass@localhost/db"

# Sécurité
SESSION_SECRET="clé_aléatoire_64_caractères_minimum"
ENCRYPTION_KEY="clé_fernet_32_bytes_base64"

# API externe
OPENROUTER_API_KEY="sk-or-v1-..."

# Mode production
FLASK_ENV="production"
DEBUG="False"
```

### Gunicorn - Configuration Optimale

```bash
# Nombre de workers
workers = (2 x nombre_de_CPU) + 1

# Exemple pour 2 CPU
gunicorn --workers 5 --threads 2 --timeout 120 main:app
```

### Nginx - Configuration Avancée

```nginx
# Compression gzip
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;

# Sécurité headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

### PostgreSQL - Optimisations

```sql
-- Augmenter les connexions max
ALTER SYSTEM SET max_connections = 100;

-- Optimiser la mémoire
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';

-- Redémarrer PostgreSQL
sudo systemctl restart postgresql
```

## Sécurité

### Checklist de Sécurité

- [ ] **Changer le mot de passe admin par défaut**
```python
# Via Python shell ou route admin
admin.password_hash = bcrypt.generate_password_hash('NouveauMotDePasseSécurisé').decode('utf-8')
db.session.commit()
```

- [ ] **HTTPS activé** (Let's Encrypt)
- [ ] **Firewall configuré** (UFW)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

- [ ] **PostgreSQL accessible uniquement en local**
```bash
# /etc/postgresql/14/main/pg_hba.conf
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

- [ ] **Secrets dans variables d'environnement** (pas dans le code)
- [ ] **Logs configurés** et monitored
- [ ] **Backups automatiques** activés

### Protection DDoS (Nginx)

```nginx
# Limiter les requêtes par IP
limit_req_zone $binary_remote_addr zone=general:10m rate=5r/s;
limit_req zone=general burst=10 nodelay;

# Limiter les connexions par IP
limit_conn_zone $binary_remote_addr zone=addr:10m;
limit_conn addr 10;
```

### Fail2Ban

```bash
sudo apt install -y fail2ban

# Configurer
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
```

## Maintenance

### Backups Automatiques

#### Script de Backup PostgreSQL

```bash
sudo nano /usr/local/bin/backup-jurisprudence.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/jurisprudence"
DB_NAME="jurisprudence_db"

mkdir -p $BACKUP_DIR

# Backup base de données
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup fichiers uploadés
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/jurisprudence-platform/uploads/

# Garder seulement les 30 derniers backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

Rendre exécutable :
```bash
sudo chmod +x /usr/local/bin/backup-jurisprudence.sh
```

#### Cron pour Backups Quotidiens

```bash
sudo crontab -e
```

Ajouter :
```
0 2 * * * /usr/local/bin/backup-jurisprudence.sh >> /var/log/backup-jurisprudence.log 2>&1
```

### Monitoring

#### Logs Importants

```bash
# Logs application
sudo journalctl -u jurisprudence -f

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs Gunicorn
sudo tail -f /var/log/gunicorn/access.log
sudo tail -f /var/log/gunicorn/error.log

# Logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### Métriques Système

```bash
# CPU et RAM
htop

# Espace disque
df -h

# Connexions PostgreSQL actives
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"
```

### Mises à Jour

#### Mise à Jour de l'Application

```bash
cd /var/www/jurisprudence-platform
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart jurisprudence
```

#### Mise à Jour du Système

```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

## Troubleshooting

### Problème: Application ne démarre pas

```bash
# Vérifier le statut du service
sudo systemctl status jurisprudence

# Voir les logs complets
sudo journalctl -u jurisprudence -n 100 --no-pager

# Vérifier les permissions
sudo chown -R www-data:www-data /var/www/jurisprudence-platform
```

### Problème: Erreur 502 Bad Gateway

```bash
# Vérifier que Gunicorn tourne
sudo systemctl status jurisprudence

# Vérifier la socket
ls -la /run/gunicorn/jurisprudence.sock

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log
```

### Problème: Base de données inaccessible

```bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Tester la connexion
psql -U jurisprudence -d jurisprudence_db -h localhost

# Vérifier les connexions actives
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Problème: Uploads échouent

```bash
# Vérifier les permissions du dossier uploads
sudo chown -R www-data:www-data /var/www/jurisprudence-platform/uploads
sudo chmod -R 755 /var/www/jurisprudence-platform/uploads

# Augmenter la limite Nginx
# Dans /etc/nginx/sites-available/jurisprudence
client_max_body_size 100M;
```

### Problème: Recherche IA ne fonctionne pas

```bash
# Vérifier la clé API
echo $OPENROUTER_API_KEY

# Tester manuellement
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "anthropic/claude-3.5-sonnet", "messages": [{"role": "user", "content": "test"}]}'
```

## Performance et Scaling

### Optimisations Nginx

```nginx
# Worker processes
worker_processes auto;
worker_connections 1024;

# Keep-alive
keepalive_timeout 65;
keepalive_requests 100;

# Buffer sizes
client_body_buffer_size 128k;
client_max_body_size 100M;
```

### Scaling Horizontal (Load Balancing)

Si besoin de plusieurs serveurs :

```nginx
upstream jurisprudence_cluster {
    least_conn;
    server app1.internal:5000 max_fails=3 fail_timeout=30s;
    server app2.internal:5000 max_fails=3 fail_timeout=30s;
    server app3.internal:5000 max_fails=3 fail_timeout=30s;
}

server {
    location / {
        proxy_pass http://jurisprudence_cluster;
        # ... autres configs
    }
}
```

### Redis (Cache de Session)

Pour scaling horizontal, utiliser Redis :

```bash
sudo apt install redis-server
pip install flask-session redis
```

```python
# backend/app.py
from flask_session import Session
from redis import Redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)
Session(app)
```

## Support

Pour assistance déploiement :
- Documentation technique : TECHNICAL_DOCUMENTATION.md
- Email : support@jurisprudence-platform.com
- Issues GitHub : https://github.com/votre-repo/issues

## Checklist de Déploiement

### Pré-déploiement
- [ ] Tests locaux passent
- [ ] Base de données migrée
- [ ] Variables d'environnement configurées
- [ ] Secrets générés et sécurisés
- [ ] Dépendances à jour

### Déploiement
- [ ] Application déployée
- [ ] Base de données initialisée
- [ ] Compte admin créé et testé
- [ ] HTTPS configuré
- [ ] Firewall activé

### Post-déploiement
- [ ] Application accessible
- [ ] Recherche IA fonctionnelle
- [ ] Upload PDF fonctionnel
- [ ] Authentification testée
- [ ] Backups configurés
- [ ] Monitoring activé
- [ ] Logs vérifiés

---

**Dernière mise à jour** : 2024
**Version** : 1.1
