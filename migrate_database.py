"""
Script de migration de données pour la nouvelle structure de base de données
Exécutez ce script pour migrer les anciennes données vers la nouvelle structure
"""

from backend.app import app, db
from backend.models.case import JurisprudenceCase
from sqlalchemy import text

def migrate_database():
    """
    Migre la base de données de l'ancienne structure vers la nouvelle
    """
    with app.app_context():
        print("🔄 Début de la migration de la base de données...")
        
        try:
            print("📋 Suppression de l'ancienne table si elle existe...")
            db.session.execute(text("DROP TABLE IF EXISTS jurisprudence_cases CASCADE"))
            db.session.commit()
            print("✅ Ancienne table supprimée")
            
            print("🔨 Création de la nouvelle structure de table...")
            db.create_all()
            print("✅ Nouvelle structure créée avec succès")
            
            print("\n📊 Vérification de la structure:")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'jurisprudence_cases'
                ORDER BY ordinal_position
            """))
            
            print("\nColonnes de la table jurisprudence_cases:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
            
            print("\n✅ Migration terminée avec succès!")
            print("\nVous pouvez maintenant:")
            print("  1. Utiliser l'importation en masse pour importer vos PDFs")
            print("  2. Utiliser le formulaire d'administration pour ajouter des cas")
            print("  3. Utiliser l'import PDF simple avec extraction automatique")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_database()
