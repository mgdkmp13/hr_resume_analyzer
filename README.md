# 🎯 HR Analyzer - AI Candidate Resume Analyzer

Aplikacja do analizy CV kandydatów przy użyciu Azure AI Services.

## 📋 Wymagania

- Python 3.8+
- Konto Azure z aktywną subskrypcją

## 🚀 Instalacja i uruchomienie lokalne

### 1. Utwórz środowisko wirtualne
```powershell
cd c:\Users\Magda\Desktop\private\level-up-ai\hr_analyzer
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
AZURE_OPENAI_MODEL=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 4. Uruchom aplikację
```powershell
streamlit run main.py
```

Aplikacja będzie dostępna pod adresem: http://localhost:8501

---

## ☁️ Konfiguracja w Azure Portal

### Krok 1: Azure AI Document Intelligence (Form Recognizer)

1. **Zaloguj się do Azure Portal**: https://portal.azure.com
2. Kliknij **"Create a resource"**
3. Wyszukaj **"Azure AI Document Intelligence"** (dawniej Form Recognizer)
4. Kliknij **"Create"**
5. Wypełnij formularz:
   - **Subscription**: Wybierz swoją subskrypcję
   - **Resource Group**: Utwórz nowy lub wybierz istniejący
   - **Region**: West Europe (lub najbliższy region)
   - **Name**: np. `hr-analyzer-form-recognizer`
   - **Pricing tier**: Free F0 (dla testów) lub S0 (dla produkcji)
6. Kliknij **"Review + create"** → **"Create"**
7. Po utworzeniu, przejdź do zasobu:
   - W menu bocznym wybierz **"Keys and Endpoint"**
   - Skopiuj **Endpoint** i **Key 1**
   - Wklej do pliku `.env`:
     ```
     FORM_RECOGNIZER_ENDPOINT=<endpoint>
     FORM_RECOGNIZER_KEY=<key1>
     ```

### Krok 2: Azure OpenAI Service

1. W Azure Portal kliknij **"Create a resource"**
2. Wyszukaj **"Azure OpenAI"**
3. Kliknij **"Create"**
4. Wypełnij formularz:
   - **Subscription**: Twoja subskrypcja
   - **Resource Group**: Ten sam co Form Recognizer
   - **Region**: Sweden Central, East US, lub inny dostępny
   - **Name**: np. `hr-analyzer-openai`
   - **Pricing tier**: Standard S0
5. Kliknij **"Review + create"** → **"Create"**
6. Po utworzeniu, przejdź do zasobu:
   - W menu bocznym wybierz **"Keys and Endpoint"**
   - Skopiuj **Endpoint** i **Key 1**
   - Wklej do pliku `.env`:
     ```
     AZURE_OPENAI_ENDPOINT=<endpoint>
     AZURE_OPENAI_KEY=<key1>
     ```

### Krok 3: Wdrożenie modelu GPT-4o

1. W zasobie Azure OpenAI przejdź do **"Model deployments"**
2. Kliknij **"Manage Deployments"** (otworzy się Azure OpenAI Studio)
3. Lub przejdź bezpośrednio: https://oai.azure.com/
4. Wybierz **"Deployments"** → **"Create new deployment"**
5. Wypełnij:
   - **Model**: Wybierz `gpt-4o`
   - **Deployment name**: `gpt-4o` (lub inna nazwa - ZAPISZ JĄ!)
   - **Version**: Najnowsza wersja
   - **Deployment type**: Standard
6. Kliknij **"Create"**
7. Jeśli użyłeś innej nazwy wdrożenia niż `gpt-4o`, zaktualizuj w `.env`:
   ```
   AZURE_OPENAI_MODEL=<twoja-nazwa-wdrożenia>
   ```

---

## 📁 Struktura projektu

```
hr_analyzer/
├── main.py                 # Aplikacja Streamlit (główny plik)
├── resume_parser.py        # Parser CV (Azure Document Intelligence)
├── analyzer.py             # Analiza kandydata (Azure OpenAI)
├── config.py              # Konfiguracja zmiennych środowiskowych
├── requirements.txt       # Zależności Python
├── .env                   # Zmienne środowiskowe (NIE commituj!)
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

## 💰 Koszty Azure

### Azure AI Document Intelligence (Form Recognizer)
- **Free tier (F0)**: 500 stron/miesiąc - **za darmo**
- **Standard (S0)**: $0.01 za stronę

### Azure OpenAI
- **GPT-4o**: ~$0.0025 za 1K tokenów wejściowych, ~$0.01 za 1K tokenów wyjściowych
- Przykład: Analiza 1 CV ≈ 500-1000 tokenów = **~$0.01-0.02 za analizę**

**Szacunkowy koszt testowy**: Jeśli przetestujesz 50 CV → ~$1-2

---

## 🛠️ Rozwiązywanie problemów

### Błąd: "Model deployment not found"
- Upewnij się, że w Azure OpenAI Studio utworzyłeś deployment modelu
- Sprawdź, czy `AZURE_OPENAI_MODEL` w `.env` pasuje do nazwy wdrożenia

### Błąd: "Unauthorized" lub 401
- Sprawdź, czy klucze API w `.env` są poprawne
- Upewnij się, że endpoint nie ma końcowego `/`

### Błąd: "prebuilt-resume model not available"
- Model `prebuilt-resume` może nie być dostępny we wszystkich regionach
- Spróbuj regionu: West Europe, East US, West US 2

### Błąd importu `dotenv`
```powershell
pip install python-dotenv
```

---

## 📝 Licencja

Projekt edukacyjny.
