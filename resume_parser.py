from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY
import json
import re

def parse_resume(file_path: str):
    """
    Parsuje CV używając Azure Document Intelligence.
    Model prebuilt-document ekstrahuje cały tekst, a następnie dzielimy go na sekcje.
    """
    client = DocumentAnalysisClient(
        FORM_RECOGNIZER_ENDPOINT,
        AzureKeyCredential(FORM_RECOGNIZER_KEY)
    )

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-document", document=f)
        result = poller.result()

    if not result.content or not result.content.strip():
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "full_text": "",
            "error": "Nie udało się wyciągnąć tekstu z PDF"
        }

    full_text = result.content
    
    skills = extract_section(full_text, ["skills", "umiejętności", "kompetencje", "technical skills", "technologies"])
    experience = extract_section(full_text, ["experience", "employment", "work history", "doświadczenie", "praca", "career"])
    education = extract_section(full_text, ["education", "wykształcenie", "studia", "academic"])
    
    if not skills and not experience and not education:
        text_preview = full_text[:2000] if len(full_text) > 2000 else full_text
        return {
            "skills": [],
            "experience": [text_preview],
            "education": [],
            "full_text": full_text
        }
    
    return {
        "skills": [skills] if skills else [],
        "experience": [experience] if experience else [],
        "education": [education] if education else [],
        "full_text": full_text
    }

def extract_section(text, keywords):
    """
    Ekstrahuje sekcję z tekstu na podstawie słów kluczowych nagłówków.
    """
    text_lower = text.lower()
    
    start_pos = -1
    
    for keyword in keywords:
        patterns = [
            rf'\n\s*{keyword}\s*[:：]\s*',  # "Skills:"
            rf'\n\s*{keyword}\s*\n',         # "Skills" na początku linii
            rf'\n\s*{keyword}\s*[-—]\s*',    # "Skills -"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start_pos = match.end()
                break
        
        if start_pos != -1:
            break
    
    if start_pos == -1:
        return ""
    
    remaining_text = text[start_pos:]
    
    next_header = re.search(r'\n\s*[A-Z][A-Za-z\s]{2,30}[:：\n]', remaining_text)
    
    if next_header and next_header.start() > 30:  
        section_text = remaining_text[:next_header.start()]
    else:
        section_text = remaining_text[:800]
    
    return section_text.strip()