# Emergency Triage Assistant

A clinical decision-support web application built with Flask. Helps emergency staff match symptoms to treatment protocols.

## Team CTRL+GENZ

- **Avani Ashiha S** – Backend Development, AACT Integration, Deployment
- **[Member 2 Name]** – Frontend Development, Voice Input, UI/UX
- **[Member 3 Name]** – Database Setup, Testing, Documentation

## Features

- **Voice‑Enabled Queries** – Speak clinical questions using the Web Speech API
- **Real‑Time Patient Data** – View vitals, history, allergies, and 30‑minute trends
- **Smart Protocol Matching** – TF‑IDF relevance engine ranks the best protocols
- **Massive Protocol Library** – 16 static protocols + 576,000+ ClinicalTrials.gov studies
- **Drug Safety Checks** – OpenFDA integration for contraindications
- **Clinical Notes** – Persistent notes per patient (MySQL)
- **Patient Search** – Quickly find patients by name or symptoms
- **Protocol Filtering** – Filter by keyword, priority, or source
- **Mobile Responsive** – Works on phones and tablets
- **Live Deployment** – Hosted on Render with automatic HTTPS

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Render](https://img.shields.io/badge/Deployed-Render-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![Contributors](https://img.shields.io/github/contributors/AA06-hash/Emergency_Triage-Assistant)](https://github.com/AA06-hash/Emergency_Triage-Assistant/graphs/contributors)

## 🛠️ Local Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/AA06-hash/Emergency_Triage-Assistant.git
   cd Emergency_Triage-Assistant
   
2. Create virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
3. Install dependencies

   ```bash
   pip install -r requirements.txt
   
4. Set up environment variables (create a .env file in the root):

   text
   AACT_USER=your_aact_username
   AACT_PASSWORD=your_aact_password
   DATABASE_URL=mysql+pymysql://username:password@host:port/emergency_triage
   SECRET_KEY=your_secret_key
   SCALEDOWN_API_KEY=your_key  # optional
   
5. Run the app

   ```bash
   python app.py

 6. Visit http://localhost:5000

Add API Documentation & Acknowledgements
```markdown
## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server status and uptime |
| GET | `/api/patients` | List all patients |
| GET | `/api/patients/<key>` | Get patient details |
| GET | `/api/patients/<key>/vitals-trend` | 30‑minute vital trends |
| GET | `/api/protocols` | List all static protocols |
| POST | `/api/query` | Run a triage query |
| GET | `/api/patients/search?q=` | Search patients |
| GET | `/api/notes/<patient>` | Get clinical notes |
| POST | `/api/notes/<patient>` | Add a clinical note |
| GET | `/api/aact/search?keywords=&limit=` | Search ClinicalTrials.gov |

## Acknowledgements

- [ClinicalTrials.gov](https://clinicaltrials.gov) for the AACT database
- [OpenFDA](https://open.fda.gov) for drug safety data
- [Render](https://render.com) for hosting
- [Clever Cloud](https://clever-cloud.com) for MySQL database
