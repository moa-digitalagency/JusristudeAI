import re

def clean_private_use_characters(text):
    """
    Nettoie les caractères de la plage Unicode Private Use Area (U+E000 à U+F8FF).
    Ces caractères spéciaux apparaissent parfois dans les documents PDF importés.
    """
    if not text:
        return text
    
    # Plage Unicode U+E000 à U+F8FF (Private Use Area)
    # Cette plage contient des caractères spéciaux non standards
    pattern = r'[\uE000-\uF8FF]'
    
    # Remplace ces caractères par un espace
    cleaned_text = re.sub(pattern, '', text)
    
    # Nettoie les espaces multiples consécutifs
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Nettoie les espaces en début et fin
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def clean_case_data(data):
    """
    Nettoie tous les champs textuels d'un dictionnaire de cas de jurisprudence.
    """
    if not isinstance(data, dict):
        return data
    
    text_fields = [
        'titre', 'juridiction', 'pays_ville', 'numero_decision', 'numero_dossier',
        'type_decision', 'chambre', 'theme', 'mots_cles', 'base_legale', 'source',
        'resume_francais', 'resume_arabe', 'texte_integral'
    ]
    
    for field in text_fields:
        if field in data and data[field]:
            data[field] = clean_private_use_characters(data[field])
    
    return data
