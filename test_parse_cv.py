"""
Szybki test parsowania CV - sprawdza co dokładnie zwraca Form Recognizer
"""
from resume_parser import parse_resume
import json
import sys

if len(sys.argv) < 2:
    print("Użycie: python test_parse_cv.py <ścieżka_do_cv.pdf>")
    print("\nLub spróbuj z przykładowym CV z folderu data/resumes/")
    import os
    if os.path.exists("data/resumes"):
        files = [f for f in os.listdir("data/resumes") if f.endswith('.pdf')]
        if files:
            print(f"Dostępne pliki: {', '.join(files)}")
            print(f"\nPrzykład: python test_parse_cv.py data/resumes/{files[0]}")
    sys.exit(1)

cv_path = sys.argv[1]

print("=" * 60)
print(f"PARSOWANIE CV: {cv_path}")
print("=" * 60)

try:
    resume_data = parse_resume(cv_path)
    
    print("\n✅ SUKCES! Sparsowane dane CV:")
    print("\n" + "=" * 60)
    print(json.dumps(resume_data, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    print("\n📊 PODSUMOWANIE:")
    print(f"Skills: {len(resume_data.get('skills', []))} elementów")
    print(f"Experience: {len(resume_data.get('experience', []))} elementów")
    print(f"Education: {len(resume_data.get('education', []))} elementów")
    
    print("\n🔍 TYPY DANYCH:")
    for key, value in resume_data.items():
        print(f"{key}: {type(value).__name__}")
        if isinstance(value, list) and value:
            print(f"  └─ pierwszy element: {type(value[0]).__name__}")
    
except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    import traceback
    traceback.print_exc()
