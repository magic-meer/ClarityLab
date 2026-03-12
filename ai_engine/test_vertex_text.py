import os
from google import genai
from app.config.settings import get_settings

settings = get_settings()

PROJECT_ID = settings.gcp_project_id
LOCATION = settings.gcp_location

print(f"Using Project: {PROJECT_ID}, Location: {LOCATION}")

if not PROJECT_ID or not LOCATION:
    print("Error: GCP project ID and location must be set.")
    exit(1)

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

print("\n--- Available Gemini Models ---")
models = list(client.models.list())
gemini_models = [m.name for m in models if "gemini" in m.name.lower()]

# Print the first few models to see exactly how Vertex returns their names 
for i, m_name in enumerate(gemini_models):
    print(f"[{i}] {m_name}")

print("\n--- Testing Text Generation ---")
# Pick a likely working model name structure
test_model_name = "gemini-2.5-flash"
print(f"Attempting to generate text with model: {test_model_name}...")

try:
    response = client.models.generate_content(
        model=test_model_name,
        contents="Hello, this is a test. Reply with 'Vertex AI is working!'"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"\nFailed to generate content with '{test_model_name}': {e}")
    
    # Try with the raw publisher format from models.list()
    if gemini_models:
        fallback_model = gemini_models[0].name if hasattr(gemini_models[0], 'name') else gemini_models[0]
        print(f"\nAttempting fallback with raw name: {fallback_model}...")
        try:
            response = client.models.generate_content(
                model=fallback_model,
                contents="Hello, this is a test. Reply with 'Vertex AI is working!'"
            )
            print(f"Success! Response: {response.text}")
        except Exception as e:
            print(f"Fallback failed as well: {e}")
