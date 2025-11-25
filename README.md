🛒 Shopper Agent – Setup Guide

This guide explains how to run both the Frontend and Backend services for the Shopper Agent application.

🚀 1. Frontend Setup
Requirements

Node.js (v18+ recommended)

npm

Steps
cd frontend
npm install
npm run dev


The frontend will start on the default development port (usually http://localhost:5173 or similar depending on your setup).

🧠 2. Backend Setup
Requirements

Python 3.10+

Virtual environment (recommended)

Steps
1. Install dependencies
cd backend
pip install -r requirements.txt

2. Install Playwright
playwright install


If Python Playwright CLI is not available:

python -m playwright install

3. Run the FastAPI Server
python -m uvicorn api:app --reload


This will start the backend server at:

http://127.0.0.1:8000

✅ Both servers must run simultaneously

Frontend: npm run dev

Backend: uvicorn api:app --reload
