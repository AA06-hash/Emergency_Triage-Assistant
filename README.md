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
