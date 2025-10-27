import re
import PyPDF2
from datetime import datetime
from typing import Dict, Optional
import os
import requests

class PDFExtractor:
    """Service pour extraire les informations structurées des PDFs de jurisprudence"""
    
    def __init__(self):
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        self.openrouter_url = 'https://openrouter.ai/api/v1/chat/completions'
        
        self.field_patterns = {
            'ref': [
                r'Ref\s*:?\s*(\d+)',
                r'R[ée]f[ée]rence\s*:?\s*(\d+)'
            ],
            'titre': [
                r'Titre\s*:?\s*(.+?)(?:\n\n|Ref\s*:)',
                r'(?:^|\n)(.+?)\n\s*Ref\s*:',
            ],
            'juridiction': [
                r'Juridiction\s*:?\s*(.+?)(?:\n|Pays)',
            ],
            'pays_ville': [
                r'Pays\s*[/\\]\s*Ville\s*:?\s*(.+?)(?:\n|N°)',
            ],
            'numero_decision': [
                r'N°\s*de\s*d[ée]cision\s*:?\s*(.+?)(?:\n|Date)',
            ],
            'date_decision': [
                r'Date\s*de\s*d[ée]cision\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            ],
            'numero_dossier': [
                r'N°\s*de\s*dossier\s*:?\s*(.+?)(?:\n|Type)',
            ],
            'type_decision': [
                r'Type\s*de\s*d[ée]cision\s*:?\s*(.+?)(?:\n|Chambre)',
            ],
            'chambre': [
                r'Chambre\s*:?\s*(.+?)(?:\n|Abstract|Th)',
            ],
            'theme': [
                r'Th[èe]me\s*:?\s*(.+?)(?:\n\n|Mots\s*cl[ée]s)',
            ],
            'mots_cles': [
                r'Mots\s*cl[ée]s\s*:?\s*(.+?)(?:\n\n|Base\s*l[ée]gale)',
            ],
            'base_legale': [
                r'Base\s*l[ée]gale\s*:?\s*(.+?)(?:\n\n|Source|R[ée]sum[ée])',
                r'Article\(s\)\s*:?\s*(.+?)(?:\n\n|Source)',
            ],
            'source': [
                r'Source\s*:?\s*(.+?)(?:\n\n|R[ée]sum[ée])',
            ],
        }
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extrait tout le texte d'un fichier PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            return text
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du texte PDF: {str(e)}")
    
    def extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extrait un champ spécifique du texte en utilisant les patterns de regex"""
        patterns = self.field_patterns.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                value = re.sub(r'\s+', ' ', value)
                return value
        
        return None
    
    def extract_resume_francais(self, text: str) -> Optional[str]:
        """Extrait le résumé en français"""
        patterns = [
            r'R[ée]sum[ée]\s*en\s*fran[çc]ais\s*:?\s*(.+?)(?:\n\n\n|R[ée]sum[ée]\s*en\s*arabe)',
            r'R[ée]sum[ée]\s*en\s*fran[çc]ais\s*(.+?)(?=R[ée]sum[ée]\s*en\s*arabe)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                resume = match.group(1).strip()
                resume = re.sub(r'\n+', ' ', resume)
                resume = re.sub(r'\s+', ' ', resume)
                return resume
        
        return None
    
    def extract_resume_arabe(self, text: str) -> Optional[str]:
        """Extrait le résumé en arabe"""
        patterns = [
            r'R[ée]sum[ée]\s*en\s*arabe\s*:?\s*(.+?)(?:\n\n\n|Texte\s*int[ée]gral|ﺑﺎﺳﻢ\s*ﺟﻼﻟﺔ)',
            r'ﺐﺣﺎﺴﻟا\s*ﻊﻴﻗﻮﺗ\s*ﺮﻳوﺰﺗ(.+?)(?=Texte\s*int[ée]gral|ﺑﺎﺳﻢ\s*ﺟﻼﻟﺔ)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        arabic_start = text.find('R') if 'Résumé en arabe' in text else -1
        if arabic_start > 0:
            arabic_section = text[arabic_start:]
            arabic_match = re.search(r'[ء-ي].+', arabic_section, re.DOTALL)
            if arabic_match:
                end_markers = ['Texte intégral', 'ﺑﺎﺳﻢ ﺟﻼﻟﺔ']
                arabic_text = arabic_match.group(0)
                for marker in end_markers:
                    if marker in arabic_text:
                        arabic_text = arabic_text.split(marker)[0]
                return arabic_text.strip()
        
        return None
    
    def extract_texte_integral(self, text: str) -> Optional[str]:
        """Extrait le texte intégral de la décision"""
        patterns = [
            r'Texte\s*int[ée]gral\s*:?\s*(.+)',
            r'ﺑﺎﺳﻢ\s*ﺟﻼﻟﺔ\s*اﻟﻤﻠﻚ\s*وﻃﺒﻘﺎ\s*ﻟﻠﻘﺎﻧﻮن(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date dans différents formats"""
        if not date_str:
            return None
        
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%d/%m/%y',
            '%d-%m-%y',
            '%Y-%m-%d',
            '%d.%m.%Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def extract_with_ai(self, text: str) -> Dict[str, any]:
        """Utilise l'IA pour extraire les champs de manière intelligente"""
        if not self.openrouter_api_key:
            return {}
        
        try:
            prompt = f"""Extrait les informations suivantes du texte juridique marocain ci-dessous. Réponds UNIQUEMENT en JSON valide sans texte additionnel:

{{
  "ref": "numéro de référence",
  "titre": "titre du cas",
  "juridiction": "juridiction",
  "pays_ville": "pays/ville",
  "numero_decision": "numéro de décision",
  "date_decision": "date au format DD/MM/YYYY",
  "numero_dossier": "numéro de dossier",
  "type_decision": "type de décision",
  "chambre": "chambre",
  "theme": "thème",
  "mots_cles": "mots clés",
  "base_legale": "base légale",
  "source": "source"
}}

Texte à analyser:
{text[:4000]}"""

            response = requests.post(
                self.openrouter_url,
                headers={
                    'Authorization': f'Bearer {self.openrouter_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                import json
                ai_data = json.loads(content)
                return ai_data
        except Exception as e:
            print(f"Erreur IA: {e}")
        
        return {}
    
    def extract_all_fields(self, pdf_file) -> Dict[str, any]:
        """Extrait tous les champs d'un PDF de jurisprudence"""
        try:
            text = self.extract_text_from_pdf(pdf_file)
            
            extracted_data = {
                'ref': self.extract_field(text, 'ref'),
                'titre': self.extract_field(text, 'titre'),
                'juridiction': self.extract_field(text, 'juridiction'),
                'pays_ville': self.extract_field(text, 'pays_ville'),
                'numero_decision': self.extract_field(text, 'numero_decision'),
                'numero_dossier': self.extract_field(text, 'numero_dossier'),
                'type_decision': self.extract_field(text, 'type_decision'),
                'chambre': self.extract_field(text, 'chambre'),
                'theme': self.extract_field(text, 'theme'),
                'mots_cles': self.extract_field(text, 'mots_cles'),
                'base_legale': self.extract_field(text, 'base_legale'),
                'source': self.extract_field(text, 'source'),
                'resume_francais': self.extract_resume_francais(text),
                'resume_arabe': self.extract_resume_arabe(text),
                'texte_integral': self.extract_texte_integral(text),
            }
            
            ai_data = self.extract_with_ai(text)
            for key, value in ai_data.items():
                if value and not extracted_data.get(key):
                    extracted_data[key] = value
            
            if not extracted_data['titre'] and extracted_data['theme']:
                extracted_data['titre'] = extracted_data['theme']
            
            date_str = extracted_data.get('date_decision') if isinstance(extracted_data.get('date_decision'), str) else self.extract_field(text, 'date_decision')
            parsed_date = self.parse_date(date_str) if date_str else None
            extracted_data['date_decision'] = parsed_date
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction des champs: {str(e)}")

pdf_extractor = PDFExtractor()
