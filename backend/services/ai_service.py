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
        
        cases_context = "\n\n".join([
            f"Cas #{case['case_number']}: {case['title']}\n{case['description'][:200]}..."
            for case in existing_cases[:50]
        ])
        
        prompt = f"""En tant qu'expert juridique, analysez le cas suivant et identifiez les cas similaires parmi la jurisprudence fournie.

CAS À ANALYSER:
{case_description}

JURISPRUDENCE DISPONIBLE:
{cases_context}

Répondez au format JSON avec:
1. similar_cases: liste des numéros de cas similaires (maximum 5)
2. similarity_scores: scores de similarité pour chaque cas (0-100)
3. analysis: analyse détaillée des similitudes
4. recommendations: recommandations pour la plaidoirie"""

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
                'max_tokens': 2000
            }
            
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            return {
                'success': True,
                'ai_analysis': ai_response,
                'model_used': result.get('model', 'anthropic/claude-3.5-sonnet')
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Erreur API: {str(e)}',
                'similar_cases': [],
                'analysis': 'Impossible de contacter le service IA'
            }

ai_service = AIService()
