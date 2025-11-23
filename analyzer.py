from openai import AzureOpenAI
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL, AZURE_OPENAI_API_VERSION
import json
import re
import numpy as np

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def get_embedding(text):
    """Pobiera embedding dla danego tekstu używając Azure OpenAI."""
    if not text or not text.strip():
        return None
    
    response = client.embeddings.create(
        model=AZURE_OPENAI_MODEL,
        input=text[:8000]  # Limit tokenów
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    """Oblicza podobieństwo cosinusowe między dwoma wektorami."""
    if vec1 is None or vec2 is None:
        return 0.0
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def extract_experience_years(text):
    """Ekstrahuje lata doświadczenia z tekstu - sumuje wszystkie okresy pracy."""
    text_lower = text.lower()
    
    # Wzorce dla wyraźnie podanych lat doświadczenia
    explicit_patterns = [
        r'(\d+)\+?\s*(?:years?|lat|roku|yrs?)',  # "5 years", "3+ lat", "2 yrs"
        r'(\d+)-(\d+)\s*(?:years?|lat|roku)',     # "3-5 years"
    ]
    
    max_explicit_years = 0
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if isinstance(match, tuple):
                # "3-5 years" → weź górną granicę
                years = max(int(match[0]), int(match[1]))
            else:
                years = int(match)
            max_explicit_years = max(max_explicit_years, years)
    
    # Wzorce dla dat (2020-2023, 2020-present, itp.)
    # Zbieramy WSZYSTKIE okresy i sumujemy
    date_patterns = [
        r'(\d{4})\s*[-–—]\s*(\d{4})',           # "2020-2023"
    ]
    
    # Osobny pattern dla present/current
    present_pattern = r'(\d{4})\s*[-–—]\s*(?:present|current|now|obecnie|today)'
    
    from datetime import datetime
    current_year = datetime.now().year
    
    total_years_from_dates = 0
    
    # Przetwórz zakresy dat (2020-2023)
    for pattern in date_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            start_year = int(match[0])
            end_year = int(match[1])
            years = end_year - start_year
            total_years_from_dates += years
    
    # Przetwórz daty z "present" (2020-present)
    present_matches = re.findall(present_pattern, text_lower, re.IGNORECASE)
    for match in present_matches:
        start_year = int(match)
        years = current_year - start_year
        total_years_from_dates += years
    
    # Zwróć większą wartość: jawnie podane lata lub suma okresów pracy
    return max(max_explicit_years, total_years_from_dates)

def extract_seniority_level(text):
    """Ekstrahuje poziom zaawansowania z tekstu."""
    text_lower = text.lower()
    
    # Wzorce dla poziomów
    if re.search(r'\b(senior|sr\.|lead|principal|architect|expert)\b', text_lower):
        return 'senior'
    elif re.search(r'\b(mid|middle|regular|intermediate)\b', text_lower):
        return 'mid'
    elif re.search(r'\b(junior|jr\.|entry[- ]level|trainee|intern|młodszy)\b', text_lower):
        return 'junior'
    
    return None

def extract_keywords(text):
    """Ekstrahuje kluczowe słowa z tekstu (w tym techniczne)."""
    # Usuń znaki specjalne ale zachowaj +, #, ++ dla technologii
    text = text.lower()
    
    # Wydobądź słowa i skróty techniczne
    words = re.findall(r'\b[a-z0-9+#\.]{2,}\b', text)
    
    # Rozszerzona lista stop words
    stop_words = {
        'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'were', 'been',
        'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 'can', 'must',
        'but', 'not', 'all', 'any', 'some', 'such', 'than', 'too', 'very', 'just',
        'you', 'your', 'our', 'their', 'his', 'her', 'its', 'who', 'what', 'where', 'when',
        'why', 'how', 'they', 'them', 'these', 'those', 'then', 'now', 'only', 'also',
        'więc', 'oraz', 'jako', 'przez', 'przy', 'nad', 'pod', 'czy', 'lub', 'jak',
        'senior', 'junior', 'mid', 'middle', 'years', 'year', 'lat', 'lata'  # Usuń poziomy z keywords
    }
    
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return set(keywords)

def normalize_tech_term(term):
    """Normalizuje terminy techniczne do wspólnych grup."""
    term_lower = term.lower()
    
    # Grupy SQL - wszystkie SQL-e są kompatybilne
    sql_variants = ['sql', 'postgresql', 'postgres', 'mysql', 'mssql', 'oracle', 'sqlite', 'mariadb']
    if any(sql in term_lower for sql in sql_variants):
        return 'sql'
    
    # Node.js warianty
    if 'node' in term_lower:
        return 'node.js'
    
    # Pozostałe bez zmian
    return term_lower

def extract_technical_terms(text):
    """Ekstrahuje techniczne terminy, frameworki, języki programowania, itp."""
    # Lista popularnych technologii (rozszerz w razie potrzeby)
    tech_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|swift|kotlin|go|rust)\b',
        r'\b(react|angular|vue|django|flask|spring|node\.?js|express|fastapi)\b',
        r'\b(docker|kubernetes|aws|azure|gcp|terraform|jenkins|gitlab|github)\b',
        r'\b(sql|postgresql|postgres|mysql|mssql|mongodb|redis|elasticsearch|oracle|sqlite|mariadb)\b',
        r'\b(git|agile|scrum|ci\/cd|devops|rest|api|microservices)\b',
        r'\b(machine learning|ai|deep learning|nlp|computer vision|data science)\b',
    ]
    
    found_terms = set()
    text_lower = text.lower()
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        found_terms.update(matches)
    
    # Normalizuj terminy (np. wszystkie SQL → 'sql')
    normalized_terms = {normalize_tech_term(term) for term in found_terms}
    
    return normalized_terms

def parse_job_requirements(job_description):
    """Rozdziela wymagania na required i nice-to-have."""
    text_lower = job_description.lower()
    
    # Znajdź sekcje
    required_section = ""
    nice_section = ""
    
    # Wzorce dla wymagań obowiązkowych
    required_patterns = [
        r'(requirements?|required|must have|must-have|wymagania|wymagane)[:\s]+(.*?)(?=nice to have|nice-to-have|preferred|optional|mile widziane|dodatkowo|$)',
        r'(obowiązkowe|necessary)[:\s]+(.*?)(?=nice to have|nice-to-have|preferred|optional|mile widziane|dodatkowo|$)',
    ]
    
    # Wzorce dla nice-to-have
    nice_patterns = [
        r'(nice to have|nice-to-have|preferred|optional|mile widziane|dodatkowo|would be plus)[:\s]+(.*?)(?=\n\n|$)',
        r'(desirable|bonus)[:\s]+(.*?)(?=\n\n|$)',
    ]
    
    # Szukaj required
    for pattern in required_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            required_section = match.group(2)
            break
    
    # Jeśli nie znaleziono sekcji required, użyj całego tekstu
    if not required_section:
        required_section = job_description
    
    # Szukaj nice-to-have
    for pattern in nice_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if match:
            nice_section = match.group(2)
            break
    
    return required_section, nice_section

def extract_text_from_field(field):
    """Ekstrahuje tekst z pola, obsługując różne formaty zwracane przez Form Recognizer."""
    if not field:
        return ""
    
    if isinstance(field, str):
        return field
    elif isinstance(field, list):
        texts = []
        for item in field:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                # Form Recognizer często zwraca dict z kluczem 'content' lub podobnym
                if 'content' in item:
                    texts.append(str(item['content']))
                elif 'value' in item:
                    texts.append(str(item['value']))
                else:
                    # Weź wszystkie wartości tekstowe z dict
                    texts.extend([str(v) for v in item.values() if isinstance(v, (str, int, float))])
            else:
                texts.append(str(item))
        return " ".join(texts)
    elif isinstance(field, dict):
        if 'content' in field:
            return str(field['content'])
        elif 'value' in field:
            return str(field['value'])
        else:
            return " ".join([str(v) for v in field.values() if isinstance(v, (str, int, float))])
    else:
        return str(field)

def analyze_candidate(resume_data, job_description):
    """
    Analizuje kandydata używając embeddings i prostych algorytmów dopasowania.
    Rozróżnia required i nice-to-have wymagania.
    """
    # Przygotuj dane z CV - obsługa różnych formatów
    skills = resume_data.get("skills", [])
    experience = resume_data.get("experience", [])
    education = resume_data.get("education", [])
    
    # Konwertuj listy na tekst z obsługą złożonych struktur
    skills_text = extract_text_from_field(skills)
    experience_text = extract_text_from_field(experience)
    education_text = extract_text_from_field(education)
    
    resume_full_text = f"{skills_text} {experience_text} {education_text}".strip()
    
    if not resume_full_text.strip():
        return {
            "score": 0,
            "strong_matches": [],
            "missing_requirements": ["Brak danych w CV"],
            "recommendation": "NO",
            "method": "embedding-based"
        }
    
    # Pobierz embeddingi
    job_embedding = get_embedding(job_description)
    resume_embedding = get_embedding(resume_full_text)
    skills_embedding = get_embedding(skills_text) if skills_text.strip() else None
    
    # Oblicz podobieństwo embeddings
    overall_similarity = cosine_similarity(job_embedding, resume_embedding)
    skills_similarity = cosine_similarity(job_embedding, skills_embedding) if skills_embedding else 0
    
    # Rozdziel wymagania na required i nice-to-have
    required_text, nice_text = parse_job_requirements(job_description)
    
    # Analiza poziomu zaawansowania
    job_seniority = extract_seniority_level(job_description)
    resume_seniority = extract_seniority_level(resume_full_text)
    
    # Analiza lat doświadczenia
    job_years = extract_experience_years(job_description)
    resume_years = extract_experience_years(resume_full_text)
    
    # Oblicz dopasowanie poziomu i doświadczenia
    seniority_match = 0.0
    experience_match = 0.0
    
    # Dopasowanie poziomu (senior > mid > junior)
    seniority_levels = {'junior': 1, 'mid': 2, 'senior': 3}
    if job_seniority and resume_seniority:
        job_level = seniority_levels.get(job_seniority, 2)
        resume_level = seniority_levels.get(resume_seniority, 2)
        
        if resume_level >= job_level:
            seniority_match = 1.0  # Kandydat ma wyższy lub równy poziom
        elif resume_level == job_level - 1:
            seniority_match = 0.7  # Jeden poziom niżej (może się nadawać)
        else:
            seniority_match = 0.3  # Zbyt duża różnica
    elif not job_seniority:
        seniority_match = 1.0  # Brak wymagania poziomu = match
    
    # Dopasowanie lat doświadczenia
    if job_years > 0:
        if resume_years >= job_years:
            experience_match = 1.0  # Spełnia wymaganie
        elif resume_years >= job_years * 0.75:
            experience_match = 0.8  # Prawie spełnia (75%+)
        elif resume_years >= job_years * 0.5:
            experience_match = 0.5  # Połowa wymaganego
        else:
            experience_match = 0.2  # Za mało doświadczenia
    else:
        experience_match = 1.0  # Brak wymagania = match
    
    # Analiza słów kluczowych
    job_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_full_text)
    
    # Analiza technicznych terminów - oddzielnie required i nice-to-have
    job_tech_required = extract_technical_terms(required_text) if required_text else set()
    job_tech_nice = extract_technical_terms(nice_text) if nice_text else set()
    job_tech_all = job_tech_required | job_tech_nice
    resume_tech = extract_technical_terms(resume_full_text)
    
    # Oblicz keyword match ratio
    common_keywords = job_keywords.intersection(resume_keywords)
    keyword_match_ratio = len(common_keywords) / len(job_keywords) if job_keywords else 0
    
    # Oblicz technical terms match - oddzielnie dla required i nice-to-have
    common_tech_required = job_tech_required.intersection(resume_tech)
    common_tech_nice = job_tech_nice.intersection(resume_tech)
    common_tech_all = job_tech_all.intersection(resume_tech)
    
    # Match ratio dla required (ważniejsze - waga 70%)
    required_match_ratio = len(common_tech_required) / len(job_tech_required) if job_tech_required else 1.0
    
    # Match ratio dla nice-to-have (mniejsza waga - 30%)
    nice_match_ratio = len(common_tech_nice) / len(job_tech_nice) if job_tech_nice else 1.0
    
    # Połączony tech match ratio z wagami
    if job_tech_required or job_tech_nice:
        tech_match_ratio = (required_match_ratio * 0.7 + nice_match_ratio * 0.3)
    else:
        tech_match_ratio = len(common_tech_all) / len(job_tech_all) if job_tech_all else 0
    
    # ULEPSZONE OBLICZANIE WYNIKU:
    # 1. Technical terms match (45%)
    # 2. Keyword match (25%)
    # 3. Experience & Seniority (20%)
    # 4. Embedding similarity (10%)
    embedding_score = (overall_similarity * 0.5 + skills_similarity * 0.5) if skills_similarity else overall_similarity
    
    # Skalowanie - embeddings często dają 0.6-0.8, więc normalizujemy
    # Zakładamy że 0.5 = 50%, 0.7 = 75%, 0.9 = 100%
    normalized_embedding = min(1.0, max(0.0, (embedding_score - 0.3) / 0.6))
    
    # Połącz seniority i experience w jeden wskaźnik
    experience_score = (seniority_match * 0.5 + experience_match * 0.5)
    
    final_score = int(
        tech_match_ratio * 45 +       # Technical: 45%
        keyword_match_ratio * 25 +    # Keywords: 25%
        experience_score * 20 +       # Experience & Seniority: 20%
        normalized_embedding * 10     # Embedding: 10%
    )
    
    # Znajdź wspólne elementy (mocne strony)
    strong_matches = []
    
    # Poziom i doświadczenie
    if seniority_match >= 0.7:
        if job_seniority and resume_seniority:
            strong_matches.append(f"✓ {resume_seniority.upper()} level match")
        if experience_match >= 0.8 and job_years > 0:
            strong_matches.append(f"✓ {resume_years}+ years experience (req: {job_years}+)")
    
    # Najpierw required tech (najważniejsze)
    if common_tech_required:
        strong_matches.extend([f"✓ {tech.upper()} (Required)" for tech in list(common_tech_required)[:3]])
    
    # Potem nice-to-have tech
    if common_tech_nice:
        strong_matches.extend([f"✓ {tech.upper()} (Nice-to-have)" for tech in list(common_tech_nice)[:2]])
    
    # Keywords
    if common_keywords:
        non_tech_keywords = common_keywords - job_tech_all
        strong_matches.extend(list(non_tech_keywords)[:2])
    
    if not strong_matches:
        strong_matches = ["Ogólne semantyczne dopasowanie profilu"]
    
    # Znajdź brakujące elementy - priorytet dla required
    missing_requirements = []
    
    # Brak poziomu/doświadczenia
    if seniority_match < 0.7 and job_seniority:
        if not resume_seniority:
            missing_requirements.append(f"⚠ {job_seniority.upper()} level not specified")
        else:
            missing_requirements.append(f"⚠ Looking for {job_seniority.upper()} (candidate: {resume_seniority})")
    
    if experience_match < 0.75 and job_years > 0:
        missing_requirements.append(f"⚠ Need {job_years}+ years (candidate: {resume_years} years)")
    
    missing_tech_required = job_tech_required - resume_tech
    if missing_tech_required:
        missing_requirements.extend([f"❌ {tech.upper()} (Required!)" for tech in list(missing_tech_required)[:3]])
    
    missing_tech_nice = job_tech_nice - resume_tech
    if missing_tech_nice:
        missing_requirements.extend([f"⚠ {tech.upper()} (Nice-to-have)" for tech in list(missing_tech_nice)[:2]])
    
    missing_keywords = job_keywords - resume_keywords - job_tech_all
    if missing_keywords and len(missing_requirements) < 6:
        important_keywords = [k for k in missing_keywords if len(k) > 4]
        missing_requirements.extend(list(important_keywords)[:2])
    
    if not missing_requirements:
        missing_requirements = ["✅ Brak kluczowych braków"]
    
    # INTELIGENTNA REKOMENDACJA:
    # YES jeśli:
    # - Technical match >= 40% LUB
    # - Final score >= 45% LUB
    # - Technical match >= 30% I keyword match >= 25%
    recommendation = "NO"
    recommendation_confidence = "low"  # low, medium, high
    
    if final_score >= 50:
        recommendation = "YES"
        recommendation_reason = "High overall match score"
        recommendation_confidence = "high"
    elif tech_match_ratio >= 0.55 and keyword_match_ratio >= 0.25:
        recommendation = "YES"
        recommendation_reason = "Strong technical + keyword match"
        recommendation_confidence = "high"
    elif tech_match_ratio >= 0.55:
        recommendation = "YES"
        recommendation_reason = "Very high technical skills match (verify other aspects)"
        recommendation_confidence = "medium"  # Żółte kółko - technical >= 55%
    elif tech_match_ratio >= 0.30 and keyword_match_ratio >= 0.30:
        recommendation = "YES"
        recommendation_reason = "Balanced technical + keyword match"
        recommendation_confidence = "medium"
    elif final_score >= 45:
        recommendation = "YES"
        recommendation_reason = "Acceptable overall match"
        recommendation_confidence = "medium"
    else:
        recommendation_reason = "Insufficient match"
        recommendation_confidence = "low"
    
    return {
        "score": final_score,
        "strong_matches": strong_matches[:6],
        "missing_requirements": missing_requirements[:6],
        "recommendation": recommendation,
        "recommendation_reason": recommendation_reason,
        "recommendation_confidence": recommendation_confidence,
        "method": "hybrid-analysis (tech + experience)",
        "similarity_scores": {
            "technical": round(tech_match_ratio, 3),
            "keywords": round(keyword_match_ratio, 3),
            "experience": round(experience_score, 3),
            "embedding": round(normalized_embedding, 3)
        },
        "debug": {
            "job_keywords_count": len(job_keywords),
            "resume_keywords_count": len(resume_keywords),
            "common_keywords_count": len(common_keywords),
            "job_tech_required_count": len(job_tech_required),
            "job_tech_nice_count": len(job_tech_nice),
            "resume_tech_count": len(resume_tech),
            "common_tech_required_count": len(common_tech_required),
            "common_tech_nice_count": len(common_tech_nice),
            "job_tech_required": list(job_tech_required),
            "job_tech_nice": list(job_tech_nice),
            "resume_tech_terms": list(resume_tech)[:10],
            "required_match_ratio": round(required_match_ratio, 3),
            "nice_match_ratio": round(nice_match_ratio, 3),
            "job_seniority": job_seniority,
            "resume_seniority": resume_seniority,
            "job_years": job_years,
            "resume_years": resume_years,
            "seniority_match": round(seniority_match, 3),
            "experience_match": round(experience_match, 3)
        }
    }