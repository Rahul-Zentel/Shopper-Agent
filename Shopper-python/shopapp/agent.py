import os
from langchain_openai import ChatOpenAI
from models import ProductSearchPreferences

def analyze_prompt(prompt: str) -> ProductSearchPreferences:
    """
    Uses OpenAI to parse a natural language prompt into structured search preferences.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    
    # Structured output using Pydantic
    structured_llm = llm.with_structured_output(ProductSearchPreferences)

    print("Agent analyzing prompt...")
    try:
        prefs = structured_llm.invoke(prompt)
        return prefs
    except Exception as e:
        print(f"Error during prompt analysis: {e}")
        # Fallback to basic query if LLM fails
        return ProductSearchPreferences(query=prompt)
