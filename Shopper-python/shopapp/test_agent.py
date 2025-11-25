from dotenv import load_dotenv
import os

load_dotenv()

# Test 1: Check if OpenAI key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key loaded: {api_key[:20] if api_key else 'NOT FOUND'}...")

# Test 2: Try to import and run agent
try:
    from agent import analyze_prompt
    print("\nAgent module imported successfully")
    
    # Try analyzing a simple prompt
    print("Testing agent analysis...")
    prefs = analyze_prompt("test product")
    print(f"Analysis successful! Query: {prefs.query}")
except Exception as e:
    import traceback
    print(f"\nAgent test failed: {e}")
    print(traceback.format_exc())
