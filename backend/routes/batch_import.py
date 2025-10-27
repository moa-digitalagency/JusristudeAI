from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from backend.models.case import db, JurisprudenceCase
from backend.utils.encryption import encryption_service
from backend.services.pdf_extractor import pdf_extractor
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime

batch_import_bp = Blueprint('batch_import', __name__)

UPLOAD_FOLDER = 'uploads/pdfs'
ALLOWED_EXTENSIONS = {'pdf'}
BATCH_SIZE = 200

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@batch_import_bp.route('/batch/upload', methods=['POST'])
@login_required
def upload_batch():
    """Première étape: Upload et sauvegarde des PDFs sur le serveur"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if 'files[]' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    files = request.files.getlist('files[]')
    
    if len(files) > BATCH_SIZE:
        return jsonify({'error': f'Maximum {BATCH_SIZE} fichiers par lot'}), 400
    
    uploaded_files = []
    errors = []
    
    batch_id = f"batch_{int(time.time())}"
    batch_folder = os.path.join(UPLOAD_FOLDER, batch_id)
    os.makedirs(batch_folder, exist_ok=True)
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(batch_folder, filename)
            
            try:
                file.save(filepath)
                uploaded_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'status': 'uploaded'
                })
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
        else:
            if file.filename:
                errors.append(f"{file.filename}: Format non valide")
    
    return jsonify({
        'batch_id': batch_id,
        'uploaded_count': len(uploaded_files),
        'uploaded_files': uploaded_files,
        'errors': errors
    }), 200

@batch_import_bp.route('/batch/process', methods=['POST'])
@login_required
def process_batch():
    """Deuxième étape: Traitement par lots avec extraction et insertion en base"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    data = request.get_json()
    batch_id = data.get('batch_id')
    start_index = data.get('start_index', 0)
    batch_size = data.get('batch_size', 10)
    
    if not batch_id:
        return jsonify({'error': 'batch_id requis'}), 400
    
    batch_folder = os.path.join(UPLOAD_FOLDER, batch_id)
    
    if not os.path.exists(batch_folder):
        return jsonify({'error': 'Batch non trouvé'}), 404
    
    files = sorted([f for f in os.listdir(batch_folder) if f.endswith('.pdf')])
    
    end_index = min(start_index + batch_size, len(files))
    files_to_process = files[start_index:end_index]
    
    results = {
        'processed': 0,
        'success': 0,
        'errors': [],
        'details': []
    }
    
    for filename in files_to_process:
        if not filename:
            continue
        filepath = os.path.join(batch_folder, filename)
        
        try:
            with open(filepath, 'rb') as pdf_file:
                extracted_data = pdf_extractor.extract_all_fields(pdf_file)
            
            if not extracted_data.get('ref'):
                results['errors'].append({
                    'filename': filename,
                    'error': 'Impossible d\'extraire la référence (ref)'
                })
                results['processed'] += 1
                continue
            
            existing_case = JurisprudenceCase.query.filter_by(ref=extracted_data['ref']).first()
            if existing_case:
                results['errors'].append({
                    'filename': filename,
                    'error': f'Cas avec ref {extracted_data["ref"]} déjà existant'
                })
                results['processed'] += 1
                continue
            
            new_case = JurisprudenceCase(
                ref=extracted_data['ref'],
                titre=extracted_data.get('titre') or f"Document {extracted_data['ref']}",
                juridiction=extracted_data.get('juridiction'),
                pays_ville=extracted_data.get('pays_ville'),
                numero_decision=extracted_data.get('numero_decision'),
                date_decision=extracted_data.get('date_decision'),
                numero_dossier=extracted_data.get('numero_dossier'),
                type_decision=extracted_data.get('type_decision'),
                chambre=extracted_data.get('chambre'),
                theme=extracted_data.get('theme'),
                mots_cles=extracted_data.get('mots_cles'),
                base_legale=extracted_data.get('base_legale'),
                source=extracted_data.get('source'),
                resume_francais_encrypted=encryption_service.encrypt(extracted_data.get('resume_francais', '')) if extracted_data.get('resume_francais') else None,
                resume_arabe_encrypted=encryption_service.encrypt(extracted_data.get('resume_arabe', '')) if extracted_data.get('resume_arabe') else None,
                texte_integral_encrypted=encryption_service.encrypt(extracted_data.get('texte_integral', '')) if extracted_data.get('texte_integral') else None,
                pdf_file_path=filepath,
                created_by=current_user.id
            )
            
            db.session.add(new_case)
            db.session.commit()
            
            results['success'] += 1
            results['details'].append({
                'filename': filename,
                'ref': extracted_data['ref'],
                'titre': extracted_data.get('titre', 'Sans titre')
            })
            
        except Exception as e:
            results['errors'].append({
                'filename': filename,
                'error': str(e)
            })
        
        results['processed'] += 1
    
    return jsonify({
        'batch_id': batch_id,
        'total_files': len(files),
        'start_index': start_index,
        'end_index': end_index,
        'processed': results['processed'],
        'success': results['success'],
        'errors_count': len(results['errors']),
        'errors': results['errors'],
        'details': results['details'],
        'has_more': end_index < len(files),
        'next_index': end_index if end_index < len(files) else None
    }), 200

@batch_import_bp.route('/batch/status/<batch_id>', methods=['GET'])
@login_required
def get_batch_status(batch_id):
    """Obtenir le statut d'un batch"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    batch_folder = os.path.join(UPLOAD_FOLDER, batch_id)
    
    if not os.path.exists(batch_folder):
        return jsonify({'error': 'Batch non trouvé'}), 404
    
    files = [f for f in os.listdir(batch_folder) if f.endswith('.pdf')]
    
    return jsonify({
        'batch_id': batch_id,
        'total_files': len(files),
        'files': files
    }), 200

@batch_import_bp.route('/batch/cleanup/<batch_id>', methods=['DELETE'])
@login_required
def cleanup_batch(batch_id):
    """Nettoyer les fichiers temporaires d'un batch après importation"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    batch_folder = os.path.join(UPLOAD_FOLDER, batch_id)
    
    if not os.path.exists(batch_folder):
        return jsonify({'error': 'Batch non trouvé'}), 404
    
    try:
        import shutil
        shutil.rmtree(batch_folder)
        return jsonify({'message': 'Batch nettoyé avec succès'}), 200
    except Exception as e:
        return jsonify({'error': f'Erreur lors du nettoyage: {str(e)}'}), 500

@batch_import_bp.route('/import/single-pdf', methods=['POST'])
@login_required
def import_single_pdf():
    """Import d'un seul PDF avec extraction automatique"""
    if not current_user.is_admin:
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Fichier PDF requis'}), 400
    
    try:
        extracted_data = pdf_extractor.extract_all_fields(file)
        
        if not extracted_data.get('ref'):
            return jsonify({
                'error': 'Impossible d\'extraire la référence (ref) du PDF',
                'extracted_data': extracted_data
            }), 400
        
        existing_case = JurisprudenceCase.query.filter_by(ref=extracted_data['ref']).first()
        if existing_case:
            return jsonify({
                'error': f'Un cas avec la référence {extracted_data["ref"]} existe déjà'
            }), 409
        
        filename = secure_filename(file.filename or 'document.pdf')
        timestamp = int(time.time())
        save_folder = os.path.join(UPLOAD_FOLDER, 'single')
        os.makedirs(save_folder, exist_ok=True)
        filepath = os.path.join(save_folder, f"{timestamp}_{filename}")
        file.seek(0)
        file.save(filepath)
        
        new_case = JurisprudenceCase(
            ref=extracted_data['ref'],
            titre=extracted_data.get('titre') or f"Document {extracted_data['ref']}",
            juridiction=extracted_data.get('juridiction'),
            pays_ville=extracted_data.get('pays_ville'),
            numero_decision=extracted_data.get('numero_decision'),
            date_decision=extracted_data.get('date_decision'),
            numero_dossier=extracted_data.get('numero_dossier'),
            type_decision=extracted_data.get('type_decision'),
            chambre=extracted_data.get('chambre'),
            theme=extracted_data.get('theme'),
            mots_cles=extracted_data.get('mots_cles'),
            base_legale=extracted_data.get('base_legale'),
            source=extracted_data.get('source'),
            resume_francais_encrypted=encryption_service.encrypt(extracted_data.get('resume_francais', '')) if extracted_data.get('resume_francais') else None,
            resume_arabe_encrypted=encryption_service.encrypt(extracted_data.get('resume_arabe', '')) if extracted_data.get('resume_arabe') else None,
            texte_integral_encrypted=encryption_service.encrypt(extracted_data.get('texte_integral', '')) if extracted_data.get('texte_integral') else None,
            pdf_file_path=filepath,
            created_by=current_user.id
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Cas importé avec succès',
            'case': new_case.to_dict(decrypt=True)
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'importation: {str(e)}'}), 500
