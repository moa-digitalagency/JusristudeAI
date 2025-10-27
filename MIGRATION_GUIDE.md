# Guide de Migration et d'Importation en Masse

## Vue d'ensemble

Ce guide documente la refonte complète du système de base de données et d'importation pour la Plateforme de Jurisprudence IA. Le système peut maintenant gérer l'importation de 200 PDFs à la fois avec extraction automatique de tous les champs structurés.

## Nouvelle Structure de Base de Données

### Champs ajoutés

La table `jurisprudence_cases` contient maintenant les champs suivants (20+ champs au total):

**Identification**:
- `ref` - Référence unique du cas
- `titre` - Titre du cas

**Juridiction et Localisation**:
- `juridiction` - Instance juridictionnelle (ex: Cour de Cassation)
- `pays_ville` - Pays/ville du tribunal
- `chambre` - Chambre judiciaire (ex: Chambre civile, pénale)

**Décision**:
- `numero_decision` - Numéro de la décision
- `numero_dossier` - Numéro du dossier
- `type_decision` - Type de décision (arrêt, jugement, etc.)
- `date_decision` - Date de la décision

**Classification**:
- `theme` - Thème juridique principal
- `mots_cles` - Mots-clés séparés par des virgules
- `base_legale` - Base légale (articles, lois, codes)
- `source` - Source de la jurisprudence

**Contenu (chiffré)**:
- `resume_francais_encrypted` - Résumé en français (chiffré)
- `resume_arabe_encrypted` - Résumé en arabe (chiffré)
- `texte_integral_encrypted` - Texte intégral de la décision (chiffré)

**Fichier**:
- `pdf_file_path` - Chemin vers le fichier PDF original

**Métadonnées**:
- `created_at`, `updated_at`, `created_by`

## Migration des Données Existantes

### Script de Migration Sécurisé

**Fichier**: `migrate_database_safe.py`

Ce script effectue une migration sécurisée des données existantes:

1. **Sauvegarde automatique** des données dans `backup_jurisprudence_cases.json`
2. **Ajout des nouveaux champs** à la table existante (pas de DROP TABLE)
3. **Conversion des anciennes données** vers la nouvelle structure:
   - `case_number` → `ref`
   - `title` → `titre`
   - `court` → `juridiction`
   - `category` → `theme`
   - `keywords` → `mots_cles`
   - `description_encrypted` → `resume_francais_encrypted`
   - `decision_encrypted` → `texte_integral_encrypted`
4. **Rollback automatique** en cas d'erreur

### Exécution de la Migration

```bash
python migrate_database_safe.py
```

**Important**: Une sauvegarde JSON sera créée avant toute modification. En cas de problème, les données peuvent être restaurées à partir de ce fichier.

## Extraction Automatique de PDFs

### Format de PDF Supporté

Le système extrait automatiquement les champs des PDFs structurés selon le format marocain:

```
Ref: JU2024001
Titre: Affaire X contre Y
Juridiction: Cour de Cassation
Pays/Ville: Maroc/Rabat
Numéro de décision: 123/2024
Date de décision: 15/03/2024
Numéro de dossier: 456/2023
Type de décision: Arrêt
Chambre: Chambre civile
Thème: Droit commercial
Mots clés: contrat, responsabilité, dommages
Base légale: Art. 230 DOC, Art. 124 Code de commerce
Source: Cour de Cassation
Résumé (en français): [texte du résumé...]
Résumé (en arabe): [texte du résumé...]
Texte intégral: [texte complet de la décision...]
```

### Service d'Extraction

**Fichier**: `backend/services/pdf_extractor.py`

Le service utilise:
- Expressions régulières pour extraire les champs structurés
- PyPDF2 pour lire le contenu des PDFs
- Chiffrement automatique des champs sensibles (résumés et texte intégral)

## Importation en Masse

### Fonctionnalités

Le système d'importation en masse (`backend/routes/batch_import.py`) permet:

1. **Upload de 200 PDFs simultanément** via l'interface web
2. **Traitement par lots de 10 fichiers** pour éviter les timeouts
3. **Extraction automatique** de tous les champs structurés
4. **Progression en temps réel** avec statut de traitement
5. **Rapport détaillé** des succès et échecs

### Utilisation

1. Accédez à la nouvelle interface d'administration: `/admin-new`
2. Cliquez sur "Importation en Masse"
3. Sélectionnez jusqu'à 200 fichiers PDF
4. Cliquez sur "Démarrer l'Importation"
5. Suivez la progression en temps réel

### Endpoints API

```
POST /api/batch-import/upload
- Upload de fichiers multiples (max 200)
- Retourne: ID de session d'importation

GET /api/batch-import/status/<session_id>
- Récupère le statut de l'importation
- Retourne: progression, succès, échecs

POST /api/batch-import/process/<session_id>
- Lance le traitement des fichiers uploadés
- Traitement asynchrone par lots de 10
```

## Nouvelle Interface d'Administration

**Fichiers**: 
- `frontend/templates/admin_new.html`
- `frontend/static/js/admin_new.js`

### Fonctionnalités

1. **Formulaire complet** avec tous les 20+ champs
2. **Import PDF simple** avec extraction automatique
3. **Importation en masse** avec suivi de progression
4. **Gestion des cas existants**
5. **Statistiques** du système

### Accès

URL: `/admin-new`

(Nécessite une authentification avec compte administrateur)

## Sécurité

### Chiffrement

Les champs sensibles sont automatiquement chiffrés avec Fernet:
- Résumés (français et arabe)
- Texte intégral des décisions
- Historique de recherche

### Variables d'Environnement

Assurez-vous que ces variables sont définies:
- `DATABASE_URL` - Connexion PostgreSQL
- `ENCRYPTION_KEY` - Clé de chiffrement Fernet
- `SECRET_KEY` - Clé de session Flask
- `OPENROUTER_API_KEY` - API pour la recherche IA

## Performances

### Optimisations

1. **Traitement par lots** (10 fichiers à la fois) pour éviter les timeouts
2. **Indexation** sur les champs de recherche fréquents (ref, date_decision, juridiction)
3. **Chiffrement sélectif** - seuls les champs sensibles sont chiffrés
4. **Sauvegarde incrémentale** - chaque fichier est sauvegardé individuellement

### Limites

- **Maximum 200 PDFs** par session d'importation
- **Taille maximale**: Selon la configuration Flask (16MB par défaut)
- **Temps de traitement**: ~2-3 secondes par PDF

## Dépannage

### Problèmes Courants

**Timeout lors de l'importation**:
- Réduisez le nombre de fichiers par lot
- Vérifiez la taille des PDFs

**Extraction incomplète**:
- Vérifiez le format du PDF
- Assurez-vous que les champs sont bien structurés
- Consultez les logs pour les détails

**Erreur de migration**:
- Vérifiez le fichier de sauvegarde `backup_jurisprudence_cases.json`
- Le rollback automatique protège vos données
- Contactez l'administrateur si le problème persiste

### Logs

Consultez les logs de l'application pour plus de détails:
```bash
tail -f /tmp/logs/Server_*.log
```

## Prochaines Étapes Recommandées

1. **Testez la migration** sur une copie de staging avant la production
2. **Validez les données migrées** en comparant avec la sauvegarde JSON
3. **Importez vos PDFs** par lots de 100-200 fichiers
4. **Vérifiez l'extraction** en consultant quelques cas importés
5. **Configurez la surveillance** pour détecter les problèmes en production

## Support

Pour toute question ou problème:
1. Consultez ce guide
2. Vérifiez les logs de l'application
3. Examinez le fichier de sauvegarde JSON
4. Contactez l'équipe technique
