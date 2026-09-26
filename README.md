# FitBuddy – AI Fitness Plan Generator

FastAPI + Gemini app that generates a 7-day workout plan and a nutrition tip,
updates the plan from user feedback, and shows an admin dashboard of all users.

## Run

```bash
cd fitbuddy
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then put your real GOOGLE_API_KEY in .env
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- Admin dashboard: http://127.0.0.1:8000/view-all-users
- API docs (Swagger): http://127.0.0.1:8000/docs

## Notes

- Drop a gym photo at `app/static/images/gym-bg.jpg` for the background.
  Without it the pages fall back to a dark gradient.
- `fitbuddy.db` is created automatically on first run.
- Model names default to `gemini-1.5-pro` / `gemini-1.5-flash`. If Google has
  retired them, set `GEMINI_PRO_MODEL` / `GEMINI_FLASH_MODEL` in `.env`.
