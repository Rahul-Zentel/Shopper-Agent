import os
from langchain_openai import ChatOpenAI
from .models import ProductSearchPreferences

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

def generate_quick_notes(products: list) -> str:
    """
    Generates a concise summary of the top products found.
    """
    if not products:
        return "No products found to summarize."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Quick notes unavailable (API key missing)."

    try:
        # Take top 5 products for summary
        top_products = products[:5]
        product_summaries = []
        for p in top_products:
            price_str = f"{p.currency} {p.price}" if p.price else "Price N/A"
            product_summaries.append(f"- {p.title} ({price_str})")
        
        products_text = "\n".join(product_summaries)
        
        prompt = (
            f"Here are the top products found for a search:\n{products_text}\n\n"
            "Write a 'Quick Notes' summary (max 3-4 bullet points) highlighting the key features, "
            "specs, or value propositions of these options. Keep it helpful for a shopper. "
            "Do not mention specific product names in the bullets if possible, focus on the range of options available."
        )

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating quick notes: {e}")
        return "Could not generate quick notes at this time."
