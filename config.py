import os
from dotenv import load_dotenv

load_dotenv()

FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT", "https://<your-form-recognizer-endpoint>.cognitiveservices.azure.com/")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY", "<your-form-recognizer_key>")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://swedencentral.api.cognitive.microsoft.com/")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "<your-azure_openai_key>")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")