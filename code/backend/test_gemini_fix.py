import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env to get key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ No API key found in .env")
    exit(1)

genai.configure(api_key=api_key)

print(f"SDK Version: {genai.__version__}")

print("\n--- Listing Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")

print("\n--- Testing Generation ---")
models_to_try = [
    'gemini-1.5-flash',
    'models/gemini-1.5-flash',
    'gemini-pro',
    'models/gemini-pro',
    'gemini-1.5-flash-latest'
]

for model_name in models_to_try:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, are you working?")
        print(f"✅ SUCCESS with {model_name}!")
        print(f"Response: {response.text[:50]}...")
        break # Stop after first success
    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")
