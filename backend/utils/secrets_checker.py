import os
import sys
from typing import List, Dict, Any

class SecretsChecker:
    """Vérifie systématiquement que tous les secrets requis sont définis"""
    
    REQUIRED_SECRETS = {
        'SESSION_SECRET': {
            'description': 'Clé secrète pour les sessions Flask',
            'critical': True
        },
        'ENCRYPTION_KEY': {
            'description': 'Clé de chiffrement pour les données sensibles',
            'critical': True,
            'help': "Générez avec: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        },
        'DATABASE_URL': {
            'description': 'URL de connexion à la base de données PostgreSQL',
            'critical': True
        },
        'OPENROUTER_API_KEY': {
            'description': 'Clé API pour OpenRouter (analyse IA)',
            'critical': False,
            'help': 'Obtenez votre clé sur https://openrouter.ai/'
        }
    }
    
    @classmethod
    def check_all(cls, verbose: bool = True) -> Dict[str, Any]:
        """
        Vérifie tous les secrets requis
        
        Returns:
            Dict avec les résultats de la vérification
        """
        results = {
            'all_critical_present': True,
            'all_present': True,
            'missing_critical': [],
            'missing_optional': [],
            'present': []
        }
        
        for secret_name, config in cls.REQUIRED_SECRETS.items():
            value = os.environ.get(secret_name)
            
            if value:
                results['present'].append(secret_name)
                if verbose:
                    print(f"✓ {secret_name}: Défini")
            else:
                if config['critical']:
                    results['missing_critical'].append(secret_name)
                    results['all_critical_present'] = False
                    results['all_present'] = False
                    if verbose:
                        print(f"❌ {secret_name}: MANQUANT (CRITIQUE)")
                        print(f"   Description: {config['description']}")
                        if 'help' in config:
                            print(f"   Aide: {config['help']}")
                else:
                    results['missing_optional'].append(secret_name)
                    results['all_present'] = False
                    if verbose:
                        print(f"⚠️  {secret_name}: Manquant (optionnel)")
                        print(f"   Description: {config['description']}")
                        if 'help' in config:
                            print(f"   Aide: {config['help']}")
        
        return results
    
    @classmethod
    def check_and_exit_if_missing_critical(cls):
        """Vérifie les secrets et quitte si des secrets critiques manquent"""
        print("\n" + "="*60)
        print("VÉRIFICATION DES SECRETS ET VARIABLES D'ENVIRONNEMENT")
        print("="*60 + "\n")
        
        results = cls.check_all(verbose=True)
        
        print("\n" + "="*60)
        
        if not results['all_critical_present']:
            print("❌ ERREUR: Des secrets critiques sont manquants!")
            print("   Veuillez configurer ces secrets dans Replit Secrets")
            print("="*60 + "\n")
            sys.exit(1)
        
        if not results['all_present']:
            print("⚠️  ATTENTION: Certains secrets optionnels sont manquants")
            print("   L'application fonctionnera avec des fonctionnalités limitées")
        else:
            print("✓ Tous les secrets sont correctement configurés!")
        
        print("="*60 + "\n")
        
        return results

secrets_checker = SecretsChecker()
