import google.generativeai as genai
import os
from dotenv import laod_dotenv

load_dotenv()

# 1. HARDCODE YOUR KEY HERE FOR THE TEST (Don't use os.getenv yet)
# We want to eliminate "environment variable" issues
API_KEY = os.getenv("google_api_key")

genai.configure(api_key=API_KEY)

print("----- HACKATNKER DIAGNOSTIC TOOL -----")
print(f"Library Version: {genai.__version__}")

print("\n🔍 Checking Available Models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
except Exception as e:
    print(f"❌ ERROR CONNECTING: {e}")

print("--------------------------------------")
