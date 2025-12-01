# Shopper Agent - Technical Analysis

## 1. Architecture Overview
The application follows a modern **Client-Server architecture**:
- **Frontend**: A Single Page Application (SPA) built with React and Vite, serving as the user interface for entering queries and displaying product results.
- **Backend**: A Python-based REST API built with FastAPI that handles business logic, orchestrates web scraping, and integrates with AI services.

## 2. Technology Stack

### Frontend (`Shopper-frnt`)
- **Framework**: [React](https://react.dev/) (v19) - Component-based UI library.
- **Build Tool**: [Vite](https://vitejs.dev/) - Fast build tool and development server.
- **Language**: [TypeScript](https://www.typescriptlang.org/) - Typed superset of JavaScript for better developer experience and code safety.
- **Linting**: ESLint - For code quality and consistency.

### Backend (`Shopper-python/shopapp`)
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance async web framework.
- **Language**: Python 3.x.
- **Web Scraping**: [Playwright](https://playwright.dev/python/) - Browser automation tool used for reliable scraping of dynamic e-commerce sites.
- **AI & LLM**: 
    - [LangChain](https://www.langchain.com/) - Framework for developing applications powered by language models.
    - [OpenAI API](https://openai.com/) (GPT-4o-mini) - Used for natural language understanding (parsing user queries) and generation (summarizing results).
- **Concurrency**: `asyncio` - Used extensively to run multiple scrapers in parallel.
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management using Python type hints.

## 3. Detailed Workflow

### A. Request Processing (`api.py`)
1. **Entry Point**: The `/search` endpoint receives a POST request with a user query and marketplace preference (e.g., "India" or "USA").
2. **Input Analysis**: 
   - The `agent.analyze_prompt` function sends the raw user query to OpenAI (GPT-4o-mini).
   - The LLM extracts structured data: `query`, `min_price`, `max_price`, etc., returning a `ProductSearchPreferences` object.

### B. Web Scraping Strategy
The application employs a **Location-Based Scraping Strategy**:
- **Concurrency**: Scrapers are run concurrently using `asyncio.gather`. Since Playwright requires its own event loop, each scraper runs in a separate thread using `asyncio.to_thread`.
- **Marketplace Selection**:
    - **India**: Scrapes Flipkart and Amazon.in.
    - **USA**: Scrapes Walmart, Target, Amazon.com, Etsy, and Best Buy.
- **Resilience**: The system includes timeouts (120s) and error handling to ensure one failing scraper doesn't crash the entire request.

### C. Product Ranking (`ranking.py`)
- After scraping, products are aggregated into a single list.
- The `rank_products` function sorts these items based on relevance to the user's query and preferences (though the current implementation details of the ranking logic would be in `ranking.py`).

### D. AI Summarization (`agent.py`)
- The top 5 ranked products are sent to the `generate_quick_notes` function.
- An LLM generates a concise "Quick Notes" summary highlighting key features and value propositions to aid the user's decision-making.

### E. Response
- The API returns a JSON response containing:
    - `products`: List of product details (title, price, rating, image, source URL).
    - `analysis`: Summary of how the agent understood the query.
    - `quick_notes`: AI-generated summary of the findings.

## 4. Key File Structure

### Backend
- **`api.py`**: Main application entry point and route definitions.
- **`agent.py`**: Handles interactions with OpenAI for prompt analysis and result summarization.
- **`scraper.py` / `scraper_*.py`**: Contains specific scraping logic for each marketplace (e.g., `scraper_walmart.py`, `scraper_amazon.py`).
- **`models.py`**: Pydantic models defining data structures for requests, responses, and internal data transfer.
- **`ranking.py`**: Logic for sorting and prioritizing scraped products.

### Frontend
- **`src/`**: Contains the React source code (components, hooks, etc.).
- **`vite.config.ts`**: Configuration for the Vite build tool.
