from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from config import FORM_RECOGNIZER_ENDPOINT, FORM_RECOGNIZER_KEY

endpoint = FORM_RECOGNIZER_ENDPOINT
key = FORM_RECOGNIZER_KEY

client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))

print(client)