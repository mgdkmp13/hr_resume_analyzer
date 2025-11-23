"""
Testy jednostkowe dla AI HR Candidate Analyzer
Sprawdzają trafność ocen dopasowania CV do ofert pracy
"""
import unittest
from analyzer import (
    extract_technical_terms, 
    extract_keywords,
    extract_seniority_level,
    extract_experience_years,
    normalize_tech_term,
    parse_job_requirements
)

class TestTechnicalTermsExtraction(unittest.TestCase):
    """Testy ekstrakcji terminów technicznych"""
    
    def test_basic_tech_terms(self):
        """Test rozpoznawania podstawowych technologii"""
        text = "Python, JavaScript, Docker, and PostgreSQL"
        terms = extract_technical_terms(text)
        
        self.assertIn('python', terms)
        self.assertIn('javascript', terms)
        self.assertIn('docker', terms)
        self.assertIn('sql', terms)  # PostgreSQL → normalized to 'sql'
    
    def test_sql_normalization(self):
        """Test normalizacji wszystkich wariantów SQL"""
        sql_variants = [
            "MySQL experience",
            "PostgreSQL database",
            "Microsoft SQL Server",
            "Oracle SQL"
        ]
        
        for variant in sql_variants:
            terms = extract_technical_terms(variant)
            self.assertIn('sql', terms, f"Failed for: {variant}")
    
    def test_frameworks_detection(self):
        """Test rozpoznawania frameworków"""
        text = "React, Django, Flask, Angular, Vue.js"
        terms = extract_technical_terms(text)
        
        self.assertIn('react', terms)
        self.assertIn('django', terms)
        self.assertIn('flask', terms)
        self.assertIn('angular', terms)
        self.assertIn('vue', terms)


class TestSeniorityLevel(unittest.TestCase):
    """Testy rozpoznawania poziomu zaawansowania"""
    
    def test_senior_detection(self):
        """Test wykrywania Senior"""
        texts = [
            "Senior Python Developer",
            "Lead Software Engineer",
            "Principal Architect"
        ]
        
        for text in texts:
            level = extract_seniority_level(text)
            self.assertEqual(level, 'senior', f"Failed for: {text}")
    
    def test_mid_detection(self):
        """Test wykrywania Mid"""
        texts = [
            "Mid-level Developer",
            "Regular Software Engineer",
            "Intermediate Python Developer"
        ]
        
        for text in texts:
            level = extract_seniority_level(text)
            self.assertEqual(level, 'mid', f"Failed for: {text}")
    
    def test_junior_detection(self):
        """Test wykrywania Junior"""
        texts = [
            "Junior Developer",
            "Entry-level Engineer",
            "Trainee Programmer"
        ]
        
        for text in texts:
            level = extract_seniority_level(text)
            self.assertEqual(level, 'junior', f"Failed for: {text}")


class TestExperienceYears(unittest.TestCase):
    """Testy ekstrakcji lat doświadczenia"""
    
    def test_explicit_years(self):
        """Test jawnie podanych lat"""
        self.assertEqual(extract_experience_years("5 years of experience"), 5)
        self.assertEqual(extract_experience_years("3+ years"), 3)
        self.assertEqual(extract_experience_years("2 yrs Python"), 2)
    
    def test_date_ranges(self):
        """Test zakresów dat"""
        self.assertEqual(extract_experience_years("2020-2023"), 3)
        self.assertEqual(extract_experience_years("2018-2020"), 2)
    
    def test_present_date(self):
        """Test dat z 'present'"""
        years = extract_experience_years("2020-present")
        self.assertGreaterEqual(years, 5)  # 2025-2020 = 5
    
    def test_multiple_periods(self):
        """Test sumowania wielu okresów pracy"""
        text = """
        Junior Dev (2023-2024)
        Intern (2022-2023)
        """
        years = extract_experience_years(text)
        self.assertEqual(years, 2)  # 1 + 1 = 2 lata


class TestRequirementsParser(unittest.TestCase):
    """Testy parsowania wymagań na required i nice-to-have"""
    
    def test_required_section(self):
        """Test wykrywania sekcji required"""
        text = """
        Requirements:
        - Python
        - SQL
        
        Nice to have:
        - Docker
        """
        required, nice = parse_job_requirements(text)
        
        self.assertIn('python', required.lower())
        self.assertIn('sql', required.lower())
        self.assertIn('docker', nice.lower())
    
    def test_no_sections(self):
        """Test gdy brak wyraźnych sekcji"""
        text = "Python, JavaScript, Docker experience needed"
        required, nice = parse_job_requirements(text)
        
        # Cały tekst jako required
        self.assertIn('python', required.lower())
        self.assertEqual(nice, "")


class TestKeywordExtraction(unittest.TestCase):
    """Testy ekstrakcji słów kluczowych"""
    
    def test_basic_keywords(self):
        """Test podstawowej ekstrakcji"""
        text = "Experience with agile development and scrum methodology"
        keywords = extract_keywords(text)
        
        self.assertIn('agile', keywords)
        self.assertIn('development', keywords)
        self.assertIn('scrum', keywords)
    
    def test_stop_words_removal(self):
        """Test usuwania stop words"""
        text = "The developer will work with the team"
        keywords = extract_keywords(text)
        
        self.assertNotIn('the', keywords)
        self.assertNotIn('will', keywords)
        self.assertIn('developer', keywords)
        self.assertIn('team', keywords)


class TestIntegrationScenarios(unittest.TestCase):
    """Testy scenariuszy integracyjnych"""
    
    def test_senior_python_match(self):
        """Test dopasowania Senior Python Developer"""
        job = "Senior Python Developer, 5+ years, Django, PostgreSQL"
        resume = "6 years as Python Developer, Django experience, MySQL"
        
        job_tech = extract_technical_terms(job)
        resume_tech = extract_technical_terms(resume)
        
        # Python i Django powinny się zgadzać
        self.assertIn('python', job_tech & resume_tech)
        self.assertIn('django', job_tech & resume_tech)
        
        # SQL powinien być znormalizowany
        self.assertIn('sql', job_tech & resume_tech)
        
        # Poziom
        self.assertEqual(extract_seniority_level(job), 'senior')
        
        # Lata doświadczenia
        job_years = extract_experience_years(job)
        resume_years = extract_experience_years(resume)
        self.assertEqual(job_years, 5)
        self.assertEqual(resume_years, 6)
        self.assertGreaterEqual(resume_years, job_years)


def run_tests():
    """Uruchom wszystkie testy"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("PODSUMOWANIE TESTÓW")
    print("="*60)
    print(f"Testy uruchomione: {result.testsRun}")
    print(f"Sukces: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Błędy: {len(result.failures)}")
    print(f"Wyjątki: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
