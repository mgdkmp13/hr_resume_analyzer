# """
# Test debugowania analizy CV
# """
# from resume_parser import parse_resume
# from analyzer import analyze_candidate
# import json

# # Test z przykładowym opisem stanowiska
# job_description = """
# Senior Python Developer
# Requirements:
# - 5+ years of Python experience
# - Django or Flask framework
# - RESTful API development
# - PostgreSQL database
# - Git version control
# - Agile/Scrum methodology
# """

# print("=" * 60)
# print("DEBUG: Analiza CV")
# print("=" * 60)

# # Jeśli masz przykładowe CV w folderze data/resumes, podaj nazwę
# # resume_path = "data/resumes/sample.pdf"
# resume_path = input("Podaj ścieżkę do pliku PDF CV (lub Enter aby pominąć): ").strip()

# if resume_path:
#     print(f"\n1. Parsowanie CV: {resume_path}")
#     try:
#         resume_data = parse_resume(resume_path)
#         print("\n📄 PARSED RESUME DATA:")
#         print(json.dumps(resume_data, indent=2, ensure_ascii=False))
        
#         print("\n" + "=" * 60)
#         print("2. Analiza kandydata...")
#         result = analyze_candidate(resume_data, job_description)
        
#         print("\n📊 ANALYSIS RESULT:")
#         print(json.dumps(result, indent=2, ensure_ascii=False))
        
#     except Exception as e:
#         print(f"❌ Błąd: {e}")
#         import traceback
#         traceback.print_exc()
# else:
#     # Test z mockowanymi danymi
#     print("\n⚠️  Brak pliku - test z mockowanymi danymi")
    
#     mock_resume = {
#         "skills": ["Python", "Django", "REST API", "PostgreSQL", "Git"],
#         "experience": ["5 years as Python Developer at Tech Company"],
#         "education": ["Bachelor in Computer Science"]
#     }
    
#     print("\n📄 MOCK RESUME DATA:")
#     print(json.dumps(mock_resume, indent=2, ensure_ascii=False))
    
#     print("\n" + "=" * 60)
#     print("2. Analiza kandydata...")
#     result = analyze_candidate(mock_resume, job_description)
    
#     print("\n📊 ANALYSIS RESULT:")
#     print(json.dumps(result, indent=2, ensure_ascii=False))

# print("\n" + "=" * 60)
# print("DEBUG ZAKOŃCZONY")
# print("=" * 60)
