"""
Script de migration de données SÉCURISÉ pour la nouvelle structure de base de données
Préserve les données existantes et les convertit vers la nouvelle structure
"""

from backend.app import app, db
from backend.models.case import JurisprudenceCase
from backend.models.user import User
from backend.utils.encryption import encryption_service
from sqlalchemy import text
from datetime import datetime
import json

def backup_existing_data():
    """Sauvegarde les données existantes avant la migration"""
    with app.app_context():
        try:
            result = db.session.execute(text("""
                SELECT * FROM jurisprudence_cases
            """))
            
            columns = result.keys()
            data = []
            for row in result:
                data.append(dict(zip(columns, row)))
            
            with open('backup_jurisprudence_cases.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ Sauvegarde de {len(data)} cas dans backup_jurisprudence_cases.json")
            return data
            
        except Exception as e:
            print(f"ℹ️  Aucune donnée existante à sauvegarder: {str(e)}")
            return []

def migrate_database_safe():
    """
    Migre la base de données de l'ancienne structure vers la nouvelle
    en préservant les données existantes
    """
    with app.app_context():
        print("🔄 Début de la migration SÉCURISÉE de la base de données...")
        
        try:
            print("\n📦 Étape 1: Sauvegarde des données existantes...")
            old_data = backup_existing_data()
            
            print("\n🔨 Étape 2: Modification de la structure de la table...")
            
            table_exists = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'jurisprudence_cases'
                )
            """)).scalar()
            
            if table_exists:
                print("  📋 Table existante détectée - ajout des nouveaux champs...")
                
                existing_columns = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'jurisprudence_cases'
                """)).fetchall()
                existing_column_names = [col[0] for col in existing_columns]
                
                new_columns = [
                    ("ref", "VARCHAR(50)"),
                    ("juridiction", "VARCHAR(200)"),
                    ("pays_ville", "VARCHAR(200)"),
                    ("numero_decision", "VARCHAR(100)"),
                    ("numero_dossier", "VARCHAR(100)"),
                    ("type_decision", "VARCHAR(100)"),
                    ("chambre", "VARCHAR(100)"),
                    ("theme", "TEXT"),
                    ("base_legale", "TEXT"),
                    ("source", "VARCHAR(200)"),
                    ("resume_francais_encrypted", "TEXT"),
                    ("resume_arabe_encrypted", "TEXT"),
                    ("texte_integral_encrypted", "TEXT"),
                    ("pdf_file_path", "VARCHAR(500)"),
                    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ]
                
                for col_name, col_type in new_columns:
                    if col_name not in existing_column_names:
                        try:
                            db.session.execute(text(f"""
                                ALTER TABLE jurisprudence_cases 
                                ADD COLUMN {col_name} {col_type}
                            """))
                            print(f"  ✅ Colonne {col_name} ajoutée")
                        except Exception as e:
                            print(f"  ⚠️  {col_name}: {str(e)}")
                
                print("\n🔄 Étape 3: Migration des données existantes...")
                
                if 'case_number' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET ref = case_number 
                        WHERE ref IS NULL AND case_number IS NOT NULL
                    """))
                    print("  ✅ Données case_number → ref migrées")
                
                if 'title' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET titre = title 
                        WHERE titre IS NULL AND title IS NOT NULL
                    """))
                    print("  ✅ Données title → titre migrées")
                
                if 'court' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET juridiction = court 
                        WHERE juridiction IS NULL AND court IS NOT NULL
                    """))
                    print("  ✅ Données court → juridiction migrées")
                
                if 'category' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET theme = category 
                        WHERE theme IS NULL AND category IS NOT NULL
                    """))
                    print("  ✅ Données category → theme migrées")
                
                if 'keywords' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET mots_cles = keywords 
                        WHERE mots_cles IS NULL AND keywords IS NOT NULL
                    """))
                    print("  ✅ Données keywords → mots_cles migrées")
                
                if 'description_encrypted' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET resume_francais_encrypted = description_encrypted 
                        WHERE resume_francais_encrypted IS NULL AND description_encrypted IS NOT NULL
                    """))
                    print("  ✅ Données description → résumé français migrées")
                
                if 'decision_encrypted' in existing_column_names:
                    db.session.execute(text("""
                        UPDATE jurisprudence_cases 
                        SET texte_integral_encrypted = decision_encrypted 
                        WHERE texte_integral_encrypted IS NULL AND decision_encrypted IS NOT NULL
                    """))
                    print("  ✅ Données decision → texte intégral migrées")
                
                db.session.commit()
                print("\n  ✅ Migration des données terminée")
                
            else:
                print("  📋 Nouvelle table - création de la structure complète...")
                db.create_all()
                print("  ✅ Structure créée")
            
            print("\n📊 Étape 4: Vérification de la structure finale:")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'jurisprudence_cases'
                ORDER BY ordinal_position
            """))
            
            print("\nColonnes de la table jurisprudence_cases:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
            
            case_count = db.session.execute(text("SELECT COUNT(*) FROM jurisprudence_cases")).scalar()
            print(f"\n📈 Total de cas dans la base: {case_count}")
            
            print("\n✅ Migration SÉCURISÉE terminée avec succès!")
            print("\n📝 Prochaines étapes:")
            print("  1. Vérifier les données migrées")
            print("  2. Utiliser l'importation en masse pour les nouveaux PDFs")
            print("  3. Ajouter manuellement les nouveaux champs manquants si nécessaire")
            print(f"\n💾 Sauvegarde disponible dans: backup_jurisprudence_cases.json")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration: {str(e)}")
            db.session.rollback()
            print("\n⚠️  Les données n'ont pas été modifiées grâce au rollback")
            raise

if __name__ == '__main__':
    migrate_database_safe()
