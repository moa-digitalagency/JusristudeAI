"""
Script d'initialisation des rôles et permissions par défaut
"""
from backend.models.role import db, Role, Permission

def initialize_roles_and_permissions(app):
    """Initialise les rôles et permissions par défaut"""
    with app.app_context():
        # Créer les permissions si elles n'existent pas
        permissions_data = [
            # Permissions pour la recherche et l'analyse
            {'name': 'search_cases', 'description': 'Effectuer des recherches de jurisprudence', 'category': 'Recherche'},
            {'name': 'view_case_analysis', 'description': 'Voir l\'analyse des cas', 'category': 'Recherche'},
            
            # Permissions pour la gestion des cas
            {'name': 'view_cases', 'description': 'Voir la liste des cas', 'category': 'Cas'},
            {'name': 'view_case_details', 'description': 'Voir les détails d\'un cas', 'category': 'Cas'},
            {'name': 'create_case', 'description': 'Créer un nouveau cas', 'category': 'Cas'},
            {'name': 'edit_case', 'description': 'Modifier un cas', 'category': 'Cas'},
            {'name': 'delete_case', 'description': 'Supprimer un cas', 'category': 'Cas'},
            {'name': 'import_cases', 'description': 'Importer des cas en batch', 'category': 'Cas'},
            
            # Permissions d'administration
            {'name': 'manage_users', 'description': 'Gérer les utilisateurs', 'category': 'Administration'},
            {'name': 'manage_roles', 'description': 'Gérer les rôles et permissions', 'category': 'Administration'},
            {'name': 'view_statistics', 'description': 'Voir les statistiques', 'category': 'Administration'},
            {'name': 'access_admin_panel', 'description': 'Accéder au panneau d\'administration', 'category': 'Administration'},
        ]
        
        created_permissions = {}
        for perm_data in permissions_data:
            perm = Permission.query.filter_by(name=perm_data['name']).first()
            if not perm:
                perm = Permission(**perm_data)
                db.session.add(perm)
                print(f"✓ Permission créée: {perm_data['name']}")
            created_permissions[perm_data['name']] = perm
        
        db.session.commit()
        
        # Créer le rôle "Juriste" (rôle par défaut)
        juriste_role = Role.query.filter_by(name='Juriste').first()
        if not juriste_role:
            juriste_role = Role(
                name='Juriste',
                description='Juriste avec accès à la recherche et à l\'analyse uniquement',
                is_system=True
            )
            # Le juriste ne peut que rechercher et voir l'analyse
            juriste_role.permissions = [
                created_permissions['search_cases'],
                created_permissions['view_case_analysis']
            ]
            db.session.add(juriste_role)
            print("✓ Rôle 'Juriste' créé")
        
        # Créer le rôle "Administrateur"
        admin_role = Role.query.filter_by(name='Administrateur').first()
        if not admin_role:
            admin_role = Role(
                name='Administrateur',
                description='Administrateur avec tous les droits',
                is_system=True
            )
            # L'admin a toutes les permissions
            admin_role.permissions = list(created_permissions.values())
            db.session.add(admin_role)
            print("✓ Rôle 'Administrateur' créé")
        
        # Créer le rôle "Gestionnaire"
        manager_role = Role.query.filter_by(name='Gestionnaire').first()
        if not manager_role:
            manager_role = Role(
                name='Gestionnaire',
                description='Gestionnaire de cas avec droits de lecture/écriture sur les cas',
                is_system=False
            )
            # Le gestionnaire peut tout faire sauf l'administration
            manager_role.permissions = [
                created_permissions['search_cases'],
                created_permissions['view_case_analysis'],
                created_permissions['view_cases'],
                created_permissions['view_case_details'],
                created_permissions['create_case'],
                created_permissions['edit_case'],
                created_permissions['delete_case'],
                created_permissions['import_cases'],
                created_permissions['view_statistics']
            ]
            db.session.add(manager_role)
            print("✓ Rôle 'Gestionnaire' créé")
        
        db.session.commit()
        print("\n✅ Initialisation des rôles et permissions terminée!")
