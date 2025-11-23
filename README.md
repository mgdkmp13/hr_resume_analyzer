# 🎯 HR Analyzer - AI Candidate Resume Analyzer

Aplikacja do analizy CV kandydatów przy użyciu Azure AI Services.

## 📋 Wymagania

- Python 3.8+
- Konto Azure z aktywną subskrypcją

## 🚀 Instalacja i uruchomienie lokalne

### 1. Utwórz środowisko wirtualne
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Zainstaluj zależności
```powershell
pip install -r requirements.txt
```

### 3. Skonfiguruj zmienne środowiskowe

Utwórz plik `.env` w głównym katalogu projektu:
```env
FORM_RECOGNIZER_ENDPOINT=https://<twoj-form-recognizer>.cognitiveservices.azure.com/
FORM_RECOGNIZER_KEY=<twoj-klucz>
AZURE_OPENAI_ENDPOINT=https://<twoj-openai>.openai.azure.com/
AZURE_OPENAI_KEY=<twoj-klucz>
AZURE_OPENAI_MODEL=text-embedding-3-large
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 4. Uruchom aplikację
```powershell
streamlit run main.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:8501

---

## 📁 Struktura projektu

```
hr_analyzer/
├── main.py                 # Aplikacja Streamlit (główny plik)
├── resume_parser.py        # Parser CV (Azure Document Intelligence)
├── analyzer.py             # Analiza kandydata (Azure OpenAI)
├── config.py              # Konfiguracja zmiennych środowiskowych
├── requirements.txt       # Zależności Python
├── .env                   # Zmienne środowiskowe
├── data/
│   ├── resumes/          # Przykładowe CV (PDF)
│   └── job_descriptions/ # Opisy stanowisk
└── README.md             # Ten plik
```

---

## 🧪 Testowanie

1. Uruchom aplikację: `streamlit run main.py`
2. Wgraj plik PDF z CV lub wybierz przykład z folderu `data/resumes/`
3. Wklej opis stanowiska w pole tekstowe
4. Kliknij **"Analyze Candidate"**
5. Aplikacja zwróci:
   - **Score**: Ocena dopasowania (0-100)
   - **Strong matches**: Mocne strony kandydata
   - **Missing requirements**: Brakujące wymagania
   - **Recommendation**: YES/NO (czy kontynuować rekrutację)

---

## 🛠️ Rozwiązywanie problemów

### Błąd: "Model deployment not found"
- Upewnij się, że w Azure OpenAI Studio utworzyłeś deployment modelu
- Sprawdź, czy `AZURE_OPENAI_MODEL` w `.env` pasuje do nazwy wdrożenia

### Błąd: "Unauthorized" lub 401
- Sprawdź, czy klucze API w `.env` są poprawne
- Upewnij się, że endpoint nie ma końcowego `/`

### Błąd importu `dotenv`
```powershell
pip install python-dotenv
```

---

## 📝 Licencja

Projekt edukacyjny.
