import requests
from backend.config import Config

class AIService:
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.api_url = Config.OPENROUTER_API_URL
    
    def find_similar_cases(self, case_description: str, existing_cases: list) -> dict:
        if not self.api_key:
            return {
                'error': 'API OpenRouter non configurée',
                'similar_cases': [],
                'analysis': 'Veuillez configurer OPENROUTER_API_KEY'
            }
        
        # Créer un index complet de tous les cas avec leurs informations
        cases_index = []
        for i, case in enumerate(existing_cases):
            # Construire un contexte riche pour chaque cas
            # Inclure le texte en français ET en arabe pour une meilleure similarité
            resume_fr = case.get('resume_francais', '')
            resume_ar = case.get('resume_arabe', '')
            
            case_text = f"""Réf: {case.get('ref', 'N/A')}
Titre: {case.get('titre', 'N/A')}
Juridiction: {case.get('juridiction', 'N/A')}
Date: {case.get('date_decision', 'N/A')}
Thème: {case.get('theme', 'N/A')}
Mots-clés: {case.get('mots_cles', 'N/A')}
Résumé FR: {(resume_fr[:300] + '...' if len(resume_fr) > 300 else resume_fr or 'N/A')}
Résumé AR: {(resume_ar[:300] + '...' if len(resume_ar) > 300 else resume_ar or 'N/A')}"""
            
            cases_index.append({
                'index': i,
                'ref': case.get('ref'),
                'titre': case.get('titre'),
                'context': case_text
            })
        
        # Limiter à 50 cas pour ne pas dépasser la limite de tokens
        cases_sample = cases_index[:50] if len(cases_index) > 50 else cases_index
        
        cases_context = "\n\n---\n\n".join([c['context'] for c in cases_sample])
        
        prompt = f"""Tu es un expert juridique spécialisé dans le droit marocain. Analyse la description du cas fournie et trouve les cas similaires dans la jurisprudence.

**INSTRUCTIONS IMPORTANTES:**
- Analyse à la fois le texte en français ET en arabe pour trouver les meilleures similarités
- Même si la requête est en français, compare-la aussi avec les résumés arabes
- Une décision avec un résumé arabe pertinent doit être incluse même si le résumé français est moins précis

CAS À ANALYSER:
{case_description}

JURISPRUDENCE DISPONIBLE ({len(cases_sample)} cas sur {len(existing_cases)} au total):
{cases_context}

Analyse les cas et identifie ceux qui sont les plus pertinents. Retourne ta réponse au format JSON strict suivant:
{{
  "similar_cases": ["réf1", "réf2", "réf3"],
  "similarity_reasons": {{
    "réf1": "raison détaillée",
    "réf2": "raison détaillée",
    "réf3": "raison détaillée"
  }},
  "analysis": "analyse globale des similitudes trouvées",
  "recommendations": "recommandations juridiques basées sur ces précédents"
}}

Trouve maximum 5 cas les plus similaires. Si aucun cas similaire n'existe, retourne une liste vide."""

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://jurisprudence-app.replit.app',
            }
            
            data = {
                'model': 'anthropic/claude-3.5-sonnet',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 3000
            }
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Extraire le JSON de la réponse
            import json
            import re
            
            # Chercher le JSON dans la réponse (entre ```json et ``` si présent, sinon chercher {})
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                json_str = json_match.group(0) if json_match else None
            else:
                json_str = json_match.group(1)
            
            if json_str:
                # Nettoyer les caractères de contrôle non échappés
                import unicodedata
                json_str_cleaned = ''.join(
                    char if ord(char) >= 32 or char in '\n\r\t' else ' '
                    for char in json_str
                )
                
                try:
                    parsed_result = json.loads(json_str_cleaned, strict=False)
                except json.JSONDecodeError as json_err:
                    # Si le parsing échoue, essayer de parser sans les newlines
                    try:
                        json_str_cleaned = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                        parsed_result = json.loads(json_str_cleaned, strict=False)
                    except:
                        raise json_err
                
                # Récupérer les cas complets correspondants
                similar_refs = parsed_result.get('similar_cases', [])
                matched_cases = []
                for case in existing_cases:
                    if case.get('ref') in similar_refs:
                        matched_cases.append(case)
                
                return {
                    'success': True,
                    'similar_cases': matched_cases,
                    'analysis': parsed_result.get('analysis', ''),
                    'recommendations': parsed_result.get('recommendations', ''),
                    'similarity_reasons': parsed_result.get('similarity_reasons', {}),
                    'total_cases_analyzed': len(cases_sample),
                    'total_cases_in_db': len(existing_cases),
                    'model_used': 'anthropic/claude-3.5-sonnet'
                }
            else:
                # Si pas de JSON trouvé, retourner la réponse brute
                return {
                    'success': True,
                    'similar_cases': [],
                    'analysis': ai_response,
                    'recommendations': '',
                    'total_cases_analyzed': len(cases_sample),
                    'total_cases_in_db': len(existing_cases)
                }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Erreur API: {str(e)}',
                'similar_cases': [],
                'analysis': 'Impossible de contacter le service IA'
            }
        except Exception as e:
            return {
                'error': f'Erreur de traitement: {str(e)}',
                'similar_cases': [],
                'analysis': 'Erreur lors de l\'analyse de la réponse'
            }

    def find_similar_cases_streaming(self, case_description: str, existing_cases: list):
        """Version avec streaming pour afficher la réflexion de l'IA en temps réel"""
        if not self.api_key:
            yield f"data: {{'error': 'API OpenRouter non configurée'}}\n\n"
            return
        
        yield f"data: {{'type': 'progress', 'message': 'Indexation des cas de jurisprudence...'}}\n\n"
        
        # Créer un index complet de tous les cas avec leurs informations
        cases_index = []
        for i, case in enumerate(existing_cases):
            # Inclure le texte en français ET en arabe pour une meilleure similarité
            resume_fr = case.get('resume_francais', '')
            resume_ar = case.get('resume_arabe', '')
            
            case_text = f"""Réf: {case.get('ref', 'N/A')}
Titre: {case.get('titre', 'N/A')}
Juridiction: {case.get('juridiction', 'N/A')}
Date: {case.get('date_decision', 'N/A')}
Thème: {case.get('theme', 'N/A')}
Mots-clés: {case.get('mots_cles', 'N/A')}
Résumé FR: {(resume_fr[:300] + '...' if len(resume_fr) > 300 else resume_fr or 'N/A')}
Résumé AR: {(resume_ar[:300] + '...' if len(resume_ar) > 300 else resume_ar or 'N/A')}"""
            
            cases_index.append({
                'index': i,
                'ref': case.get('ref'),
                'titre': case.get('titre'),
                'context': case_text
            })
        
        cases_sample = cases_index[:50] if len(cases_index) > 50 else cases_index
        
        yield f"data: {{'type': 'progress', 'message': '{len(cases_sample)} cas indexés sur {len(existing_cases)} au total'}}\n\n"
        
        cases_context = "\n\n---\n\n".join([c['context'] for c in cases_sample])
        
        prompt = f"""Tu es un expert juridique spécialisé dans le droit marocain. Analyse la description du cas fournie et trouve les cas similaires dans la jurisprudence.

**INSTRUCTIONS IMPORTANTES:**
- Analyse à la fois le texte en français ET en arabe pour trouver les meilleures similarités
- Même si la requête est en français, compare-la aussi avec les résumés arabes
- Une décision avec un résumé arabe pertinent doit être incluse même si le résumé français est moins précis

CAS À ANALYSER:
{case_description}

JURISPRUDENCE DISPONIBLE ({len(cases_sample)} cas sur {len(existing_cases)} au total):
{cases_context}

Analyse les cas et identifie ceux qui sont les plus pertinents. Retourne ta réponse au format JSON strict suivant:
{{
  "similar_cases": ["réf1", "réf2", "réf3"],
  "similarity_reasons": {{
    "réf1": "raison détaillée",
    "réf2": "raison détaillée",
    "réf3": "raison détaillée"
  }},
  "analysis": "analyse globale des similitudes trouvées",
  "recommendations": "recommandations juridiques basées sur ces précédents"
}}

Trouve maximum 5 cas les plus similaires. Si aucun cas similaire n'existe, retourne une liste vide."""

        yield f"data: {{'type': 'progress', 'message': 'Envoi de la requête à l\\'IA...'}}\n\n"
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://jurisprudence-app.replit.app',
            }
            
            data = {
                'model': 'anthropic/claude-3.5-sonnet',
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 3000,
                'stream': True
            }
            
            yield f"data: {{'type': 'progress', 'message': 'L\\'IA analyse les cas... (cela peut prendre 15-30 secondes)'}}\n\n"
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=120, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        try:
                            import json
                            chunk_data = json.loads(line_text[6:])
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    # Envoyer des mises à jour régulières
                                    if len(full_response) % 100 < 10:  # Tous les ~100 caractères
                                        yield f"data: {{'type': 'thinking', 'message': 'Réflexion en cours...'}}\n\n"
                        except:
                            continue
            
            yield f"data: {{'type': 'progress', 'message': 'Traitement de la réponse de l\\'IA...'}}\n\n"
            
            # Traiter la réponse complète
            import json
            import re
            
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', full_response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\{.*\}', full_response, re.DOTALL)
                json_str = json_match.group(0) if json_match else None
            else:
                json_str = json_match.group(1)
            
            if json_str:
                import unicodedata
                json_str_cleaned = ''.join(
                    char if ord(char) >= 32 or char in '\n\r\t' else ' '
                    for char in json_str
                )
                
                try:
                    parsed_result = json.loads(json_str_cleaned, strict=False)
                except json.JSONDecodeError:
                    json_str_cleaned = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    parsed_result = json.loads(json_str_cleaned, strict=False)
                
                # Récupérer les cas complets correspondants
                similar_refs = parsed_result.get('similar_cases', [])
                matched_cases = []
                for case in existing_cases:
                    if case.get('ref') in similar_refs:
                        matched_cases.append(case)
                
                result = {
                    'success': True,
                    'similar_cases': matched_cases,
                    'analysis': parsed_result.get('analysis', ''),
                    'recommendations': parsed_result.get('recommendations', ''),
                    'similarity_reasons': parsed_result.get('similarity_reasons', {}),
                    'total_cases_analyzed': len(cases_sample),
                    'total_cases_in_db': len(existing_cases),
                    'model_used': 'anthropic/claude-3.5-sonnet'
                }
                
                import json as json_module
                yield f"data: {{'type': 'complete', 'result': {json_module.dumps(result, ensure_ascii=False)}}}\n\n"
            else:
                yield f"data: {{'type': 'error', 'message': 'Format de réponse invalide'}}\n\n"
                
        except Exception as e:
            yield f"data: {{'type': 'error', 'message': 'Erreur: {str(e)}'}}\n\n"

ai_service = AIService()
