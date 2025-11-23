# 🎓 Instrukcja - Deployment text-embedding-3-large

## Krok 1: Utwórz deployment w Azure OpenAI Studio

1. **Przejdź do:** https://oai.azure.com/
2. Zaloguj się kontem Azure
3. W lewym menu wybierz **"Deployments"**
4. Kliknij **"+ Create new deployment"**
5. Wypełnij formularz:
   - **Select a model:** `text-embedding-3-large`
   - **Deployment name:** `text-embedding-3-large` (lub inna nazwa - ZAPISZ!)
   - **Model version:** Najnowsza dostępna
   - **Deployment type:** Standard
6. Kliknij **"Create"**
7. Poczekaj ~1-2 minuty na deployment

## Krok 2: Zaktualizuj plik .env

Jeśli użyłeś **innej nazwy** niż `text-embedding-3-large`, zmień w `.env`:

```env
AZURE_OPENAI_MODEL=<twoja-nazwa-deploymentu>
```

## Krok 3: Uruchom test

```powershell
python test_openai.py
```

Powinieneś zobaczyć:
```
✅ SUKCES! Otrzymano embedding o wymiarach: 3072
```

## Krok 4: Uruchom aplikację

```powershell
streamlit run main.py
```

---

## 🧠 Jak teraz działa aplikacja?

**Zamiast GPT-4 używamy:**
1. **Azure Document Intelligence** - parsuje CV (jak wcześniej)
2. **text-embedding-3-large** - tworzy wektory semantyczne z CV i opisu stanowiska
3. **Cosine Similarity** - oblicza podobieństwo między CV a ofertą (0-100%)
4. **Keyword Matching** - znajduje wspólne słowa kluczowe i braki

**Plusy:**
- ✅ Działa z kontem studenckim
- ✅ Tańsze niż GPT-4
- ✅ Szybkie działanie

**Minusy:**
- ⚠️ Brak złożonej analizy tekstowej (GPT lepiej rozumie kontekst)
- ⚠️ Proste dopasowanie słów kluczowych zamiast rozumienia treści

Ale dla podstawowej analizy CV to wystarczające rozwiązanie! 🎯
