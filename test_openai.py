from openai import AzureOpenAI
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL, AZURE_OPENAI_API_VERSION
import requests

print("=" * 60)
print("TEST POŁĄCZENIA Z AZURE OPENAI")
print("=" * 60)

print("\n1. KONFIGURACJA:")
print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
print(f"   API Version: {AZURE_OPENAI_API_VERSION}")
print(f"   Model (deployment): {AZURE_OPENAI_MODEL}")
print(f"   Key: {AZURE_OPENAI_KEY[:10]}...{AZURE_OPENAI_KEY[-5:]}")

print("\n2. TWORZENIE KLIENTA...")
try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    print("   ✅ Klient utworzony pomyślnie")
except Exception as e:
    print(f"   ❌ Błąd tworzenia klienta: {e}")
    exit(1)

print("\n3. SPRAWDZANIE DOSTĘPNYCH WDROŻEŃ...")
# Próba pobrania listy wdrożeń przez różne API endpoints
headers = {
    "api-key": AZURE_OPENAI_KEY,
    "Content-Type": "application/json"
}

# Próbujemy różne endpointy API
api_versions = [
    "2023-05-15",
    "2024-02-01",
    AZURE_OPENAI_API_VERSION
]

deployments_found = False
for api_ver in api_versions:
    deployments_url = f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments?api-version={api_ver}"
    
    try:
        response = requests.get(deployments_url, headers=headers)
        if response.status_code == 200:
            deployments = response.json()
            if 'data' in deployments and deployments['data']:
                print(f"   ✅ Znaleziono {len(deployments['data'])} wdrożeń (API: {api_ver}):")
                for dep in deployments['data']:
                    print(f"      - {dep.get('id', 'unknown')} (model: {dep.get('model', 'unknown')})")
                
                # Sprawdź czy nasz model istnieje
                deployment_ids = [d.get('id') for d in deployments['data']]
                if AZURE_OPENAI_MODEL in deployment_ids:
                    print(f"\n   ✅ Twoje wdrożenie '{AZURE_OPENAI_MODEL}' ISTNIEJE!")
                else:
                    print(f"\n   ❌ Wdrożenie '{AZURE_OPENAI_MODEL}' NIE ISTNIEJE!")
                    print(f"   💡 Zmień AZURE_OPENAI_MODEL w .env na jedno z powyższych")
                deployments_found = True
                break
    except:
        continue

if not deployments_found:
    print("   ⚠️  Nie można automatycznie pobrać listy wdrożeń")
    print("   💡 Sprawdź ręcznie na: https://oai.azure.com/")

print("\n4. TEST EMBEDDINGS...")
try:
    response = client.embeddings.create(
        model=AZURE_OPENAI_MODEL,
        input="Test embedding"
    )
    
    embedding = response.data[0].embedding
    print(f"   ✅ SUKCES! Otrzymano embedding o wymiarach: {len(embedding)}")
    print(f"   Model: {AZURE_OPENAI_MODEL}")
    print(f"   Pierwsze 5 wartości: {embedding[:5]}")
    
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")
    print("\n" + "=" * 60)
    print("ROZWIĄZANIE:")
    print("=" * 60)
    print("1. Upewnij się, że wdrożenie text-embedding-3-large istnieje")
    print("2. Przejdź do: https://oai.azure.com/")
    print("3. Wybierz 'Deployments' w menu")
    print("4. Sprawdź nazwę wdrożenia embedding")
    print("5. Zaktualizuj AZURE_OPENAI_MODEL w pliku .env")
    print("6. Uruchom ponownie: python test_openai.py")
    print("=" * 60)

print("\n" + "=" * 60)
print("TEST ZAKOŃCZONY")
print("=" * 60)
