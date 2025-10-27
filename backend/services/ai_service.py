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
            case_text = f"""Réf: {case.get('ref', 'N/A')}
Titre: {case.get('titre', 'N/A')}
Juridiction: {case.get('juridiction', 'N/A')}
Date: {case.get('date_decision', 'N/A')}
Thème: {case.get('theme', 'N/A')}
Mots-clés: {case.get('mots_cles', 'N/A')}
Résumé FR: {(case.get('resume_francais', '')[:300] + '...' if len(case.get('resume_francais', '')) > 300 else case.get('resume_francais', 'N/A'))}"""
            
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
            
            # Chercher le JSON dans la réponse
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed_result = json.loads(json_match.group(0))
                
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

ai_service = AIService()
