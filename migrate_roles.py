"""
Script de migration pour ajouter les tables de rôles et permissions
"""
from backend.app import app
from backend.models.user import db
from backend.models.role import Role, Permission, role_permissions
from backend.init_roles import initialize_roles_and_permissions

print("=== Migration des rôles et permissions ===\n")

with app.app_context():
    try:
        # Créer les nouvelles tables
        print("1. Création des tables roles, permissions et role_permissions...")
        db.create_all()
        print("   ✓ Tables créées\n")
        
        # Initialiser les rôles et permissions par défaut
        print("2. Initialisation des rôles et permissions par défaut...")
        initialize_roles_and_permissions(app)
        print("\n")
        
        # Vérifier que tout est en place
        roles_count = Role.query.count()
        permissions_count = Permission.query.count()
        
        print(f"3. Vérification:")
        print(f"   - {roles_count} rôles créés")
        print(f"   - {permissions_count} permissions créées")
        
        print("\n✅ Migration terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
