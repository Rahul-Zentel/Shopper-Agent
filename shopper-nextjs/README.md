# Shopper Agent - Next.js Frontend

AI-powered shopping assistant with dual-mode functionality: Scraper Mode and Deep Agent Mode.

## Features

- **Scraper Mode**: Uses web scraping (Playwright) to extract product data from multiple marketplaces
- **Deep Agent Mode**: Uses Tavily API and LangChain to intelligently search and analyze products
- Location support: India and USA marketplaces
- Real-time product search with analysis and quick notes

## Prerequisites

- Node.js 18+
- npm
- Backend API running on http://127.0.0.1:8000

## Installation

```bash
cd shopper-nextjs
npm install
```

## Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

## Running the Application

```bash
npm run dev
```

The app will be available at http://localhost:3000

## Project Structure

```
shopper-nextjs/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main application page
│   └── globals.css         # Global styles
├── components/
│   ├── SearchPage.tsx      # Search interface with mode toggle
│   ├── TasksPage.tsx       # Task progress display
│   └── ResultsPage.tsx     # Product results display
└── lib/
    ├── api.ts              # API client functions
    └── types.ts            # TypeScript type definitions
```

## Usage

1. Select a mode (Scraper or Deep Agent)
2. Choose your location (India or USA)
3. Enter your search query
4. View results with AI-powered analysis

## Mode Comparison

### Scraper Mode
- Direct web scraping from marketplaces
- Fast product extraction
- Requires Playwright browsers
- Returns structured product data

### Deep Agent Mode
- Uses Tavily for web search
- LangChain-powered analysis
- Gift ideation for vague queries
- Intelligent product ranking
- Best for discovery and recommendations
