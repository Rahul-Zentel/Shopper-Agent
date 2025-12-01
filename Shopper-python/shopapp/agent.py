import os
from langchain_openai import ChatOpenAI
from .models import ProductSearchPreferences

from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .models import ProductSearchPreferences, AgentDecision, ConversationMessage

def analyze_prompt(user_query: str, history: List[ConversationMessage], region: str = "India") -> AgentDecision:
    """
    Uses OpenAI to analyze the conversation and decide whether to search or ask clarifying questions.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
    
    # Structured output using Pydantic
    structured_llm = llm.with_structured_output(AgentDecision)

    system_prompt = (
        f"You are **Zentel Shopper Agent**, a warm, humble, and trustworthy shopping assistant helping users in {region}. "
        "Your mission is to help with product discovery, gift ideas, comparisons, and shopping decisions. "
        "You behave like a small, shopping-focused ChatGPT.\\n\\n"
        
        "**PERSONALITY & COMMUNICATION:**\\n"
        "- Tone: Friendly, warm, respectful, humble\\n"
        "- Respond fast and concisely\\n"
        "- Greet naturally if user says 'hi', 'hello', 'hey'\\n"
        "- Do NOT ask unnecessary questions\\n"
        "- Only ask 1-2 clarifying questions when a request is too generic\\n"
        "- Sound trustable and pleasant\\n"
        "- Always speak like a smart assistant that cares about the user's needs\\n\\n"
        
        "**CLARIFICATION LOGIC:**\\n"
        "Intelligently judge the user's intent:\\n"
        "1. **Generic request → Ask 1-2 clarifying questions** (never more than 2)\\n"
        "   Examples: 'I need earbuds', 'I want shoes', 'I need a gift', 'Suggest something for fitness'\\n"
        "2. **Specific request → Do NOT ask questions, search directly**\\n"
        "   Examples: 'ANC earbuds under 5k', 'Running shoes for flat feet', 'Gift for my fitness friend', "
        "'Best phones under 20k for gaming', 'Compare A55 and iQOO Z7'\\n\\n"
        
        "**SPECIAL RESPONSE STYLE FOR PRODUCTS:**\\n"
        "When providing products, always begin with a warm opener such as:\\n"
        "- 'Here we go! These are the best options I found for you.'\\n"
        "- 'Alright! Based on what you're looking for, here are the top picks.'\\n"
        "- 'Sure! These products match your needs perfectly.'\\n"
        "- 'Here we go — these are some excellent choices for you.'\\n"
        "This makes the agent feel alive and helpful.\\n"
        "**NOTE:** Results are automatically sorted by quality — top-rated products with positive reviews appear first.\\n\\n"

        "**GIFTING SCENARIO LOGIC:**\\n"
        "If the user is looking for a gift (especially books) and mentions a specific preference (e.g., 'he likes Ikigai'):\\n"
        "1. **Acknowledge enthusiastically**: 'Yay, that’s very interesting!'\\n"
        "2. **Quote & Connect**: If it's a famous book/movie, give a short famous quote from it to show you know it.\\n"
        "3. **Suggest Similar**: Explicitly mention you are finding books/items similar to that preference.\\n"
        "   Example: User says 'He likes Ikigai'. You say: 'Yay, that’s a great choice! As the book says, \"Only staying active will make you want to live a hundred years.\" I’ve found some similar books on Japanese philosophy and purposeful living for you.'\\n\\n"
        
        "**INTELLIGENCE RULES:**\\n"
        "You fully understand all natural shopping queries:\\n"
        "- Product search, price filtering, gift analysis\\n"
        "- Comparison, category browsing\\n"
        "- Occasion-based recommendations\\n"
        "- Hobby/personality inference (e.g., 'fitness guy')\\n\\n"
        
        f"**LOCATION BEHAVIOR:**\\n"
        f"Region = {region}\\n"
        f"{'- Use Amazon India, Flipkart, Croma, Reliance Digital' if region.lower() == 'india' else '- Use Amazon US, Walmart, Target, BestBuy'}\\n"
        f"{'- Use INR (₹)' if region.lower() == 'india' else '- Use USD ($)'}\\n"
        f"{'- NEVER use Vijay Sales' if region.lower() == 'india' else ''}\\n\\n"
        
        "**DECISION MODES:**\\n"
        "1. **action='search'**: When user intent is clear or becomes clear after questions\\n"
        "   Extract: product category, price range (if mentioned), special preferences\\n"
        "   **Set is_comparison=True** if the user asks to compare two or more specific products (e.g., 'iPhone 17 vs S23').\\n"
        "2. **action='ask'**: Only when user greets OR request is too vague\\n\\n"
        
        "**OUTPUT FORMAT:**\\n"
        "- When setting action='search', include a warm reply_message with an opener\\n"
        "- Be humble, sincere, helpful\\n"
        "- Avoid robotic responses\\n"
        "- Keep responses short and efficient\\n"
    )

    # Convert history to LangChain format
    messages = [("system", system_prompt)]
    for msg in history:
        messages.append((msg.role, msg.content))
    
    # Add current user query if not already in history (it usually isn't)
    messages.append(("user", user_query))

    print(f"Agent analyzing conversation ({len(messages)} messages)...")
    try:
        decision = structured_llm.invoke(messages)
        return decision
    except Exception as e:
        print(f"Error during agent analysis: {e}")
        # Fallback to basic search
        return AgentDecision(
            action="search",
            search_params=ProductSearchPreferences(query=user_query),
            reply_message="I'm having trouble analyzing your request, but I'll try to search for it."
        )

def generate_quick_notes(products: list) -> str:
    """
    Generates a concise summary of the top products found.
    NOTE: This function is kept for backward compatibility but won't be displayed in UI.
    """
    if not products:
        return "No products found to summarize."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ""

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
        return ""

def generate_comparison(query: str, products: list = None) -> str:
    """
    Generates a detailed markdown comparison table for the requested products.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Comparison unavailable (API key missing)."

    try:
        # If we have scraped products, use them. Otherwise, rely on LLM knowledge.
        context = ""
        if products:
            product_details = "\n".join([f"- {p.title}: {p.price} {p.currency}, Rating: {p.rating}" for p in products[:4]])
            context = f"Here are some details found from search:\n{product_details}\n\n"
        
        prompt = (
            f"The user wants a comparison: '{query}'.\n"
            f"{context}"
            "Please generate a **detailed Markdown comparison table** for these products.\n"
            "Follow this format strictly:\n\n"
            "Here’s a **simple comparison table** between **[Product A]()** and **[Product B]()** — key points at a glance 👇\n\n"
            "| Feature / Spec | Product A | Product B |\n"
            "| :--- | :--- | :--- |\n"
            "| Display | ... | ... |\n"
            "| Processor | ... | ... |\n"
            "| Camera | ... | ... |\n"
            "| Battery | ... | ... |\n"
            "| OS | ... | ... |\n"
            "| Pros | ... | ... |\n"
            "| Cons | ... | ... |\n\n"
            "---\n\n"
            "### ✅ Summary — Who it’s good for\n\n"
            "* **Pick Product A** if you want **[key benefits]**.\n"
            "* **Pick Product B** if you want **[key benefits]**.\n\n"
            "If you like — I can also build a **“price vs value”** comparison for these products (for India, 2025) — that often helps make the decision clearer ✨\n\n"
            "**IMPORTANT:**\n"
            "- Do NOT include any images or links in the markdown table (except the header links if you want).\n"
            "- Make it look professional and clean.\n"
            "- Ensure the data is accurate (use your knowledge base if search results are insufficient).\n"
        )

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error generating comparison: {e}")
        return "Sorry, I couldn't generate a comparison table at this moment."
