# Guide d'Importation en Masse de PDFs

## Fonctionnalité d'Import en Masse

La plateforme Jurisprudence dispose maintenant d'une fonctionnalité complète d'**importation en masse de PDFs** accessible dans le panneau d'administration.

### Accès

1. Connectez-vous avec un compte administrateur
2. Accédez à la page **Administration** via le menu de navigation
3. Cliquez sur l'onglet **"Importation en Masse"**

### Fonctionnalités

#### 1. Import en Masse (jusqu'à 200 PDFs)

**Comment l'utiliser:**

1. Cliquez sur le bouton "Sélectionner les PDFs"
2. Sélectionnez jusqu'à **200 fichiers PDF** depuis votre ordinateur
3. Cliquez sur **"Uploader les fichiers"**
4. Le système va automatiquement:
   - Uploader tous les fichiers sur le serveur
   - Extraire les informations de chaque PDF (référence, titre, juridiction, etc.)
   - Traiter les fichiers par lots de 10 pour éviter les timeouts
   - Afficher une barre de progression en temps réel
   - Stocker les données dans la base de données

**Informations extraites automatiquement:**
- Référence (ref) - **obligatoire**
- Titre
- Juridiction
- Pays/Ville
- Numéro de décision
- Date de décision
- Numéro de dossier
- Type de décision
- Chambre
- Thème
- Mots-clés
- Base légale
- Source
- Résumé en français (crypté)
- Résumé en arabe (crypté)
- Texte intégral (crypté)

**Rapport de traitement:**
- Nombre de fichiers traités avec succès
- Nombre d'erreurs
- Liste détaillée des erreurs (fichier manquant une référence, doublons, etc.)

#### 2. Import PDF Simple

Pour importer un seul PDF avec extraction automatique:

1. Cliquez sur l'onglet **"Import PDF Simple"**
2. Sélectionnez un fichier PDF
3. Cliquez sur **"Importer et Extraire"**
4. Le système extrait automatiquement toutes les informations
5. Les données sont affichées pour vérification
6. Cliquez sur **"Confirmer et Sauvegarder"** pour enregistrer

### Routes API Backend

Les endpoints suivants sont disponibles:

```
POST /api/batch/upload
- Upload de fichiers en masse
- Paramètre: files[] (multipart/form-data)
- Limite: 200 fichiers maximum

POST /api/batch/process
- Traitement par lots
- Paramètres: batch_id, start_index, batch_size
- Traitement asynchrone avec gestion de progression

GET /api/batch/status/<batch_id>
- Vérifier le statut d'un lot

DELETE /api/batch/cleanup/<batch_id>
- Nettoyer les fichiers temporaires

POST /api/import/single-pdf
- Import d'un seul PDF avec extraction automatique
- Paramètre: file (multipart/form-data)
```

### Gestion des Erreurs

Le système gère intelligemment les erreurs:

- **Référence manquante**: Le PDF est rejeté (la référence est obligatoire)
- **Doublons**: Si un cas avec la même référence existe déjà, le fichier est ignoré
- **Format invalide**: Seuls les fichiers PDF sont acceptés
- **Erreurs d'extraction**: L'erreur est enregistrée et reportée à l'utilisateur

### Sécurité

- Les données sensibles (résumés, texte intégral) sont **automatiquement cryptées** avec `ENCRYPTION_KEY`
- Seuls les administrateurs peuvent accéder à cette fonctionnalité
- Les fichiers sont stockés de manière sécurisée dans `uploads/pdfs/`

### Compte Administrateur par Défaut

- **Email**: admin@jurisprudence.com
- **Mot de passe**: Admin123!

---

## Support Technique

Pour toute question ou problème, vérifiez:
1. Que vous êtes connecté avec un compte administrateur
2. Que les variables d'environnement `ENCRYPTION_KEY` et `SESSION_SECRET` sont définies
3. Que la base de données PostgreSQL est correctement configurée
