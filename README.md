# Emergency Triage Assistant

A clinical decision-support web application built with Flask. Helps emergency staff match symptoms to treatment protocols.

## Local Development

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Visit http://localhost:5000

## Deploy to Render

1. Push code to a GitHub repository
2. On Render.com, create a new Web Service and connect your repo
3. Render auto-detects settings; click Create Web Service
4. Your app will be live at a .onrender.com URL
