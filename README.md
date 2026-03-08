# Nepal PR Seat Allocation (Sainte-Lague)

Production-ready Flask web app that:
- Fetches PR vote counts from Election Commission Nepal (`PRVoteChartResult2082.aspx` data source).
- Applies the Sainte-Lague method for House of Representatives PR seat allocation.
- Supports configurable seat count and threshold from UI and API.

## Project structure

```text
.
|-- app/
|   |-- __init__.py
|   |-- election_client.py
|   |-- seat_allocator.py
|   |-- service.py
|   |-- routes.py
|   |-- static/css/styles.css
|   `-- templates/index.html
|-- tests/test_seat_allocator.py
|-- requirements.txt
|-- render.yaml
|-- wsgi.py
`-- sainte_lague_nepal.py
```

## Local run

1. Create environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Start the app:

```bash
python wsgi.py
```

Open: `http://127.0.0.1:5000`

## API

`GET /api/allocation?seats=110&threshold=3`

## CLI (optional)

```bash
python sainte_lague_nepal.py --seats 110 --threshold 3
```

## Deploy free on Render

1. Push this repo to GitHub.
2. Go to Render dashboard -> New -> Blueprint.
3. Connect your GitHub repo and select it.
4. Render detects `render.yaml` and deploys automatically.
5. On each push to `main`, Render redeploys.

## Upload to GitHub

If this directory is not already a git repo:

```bash
git init
git add .
git commit -m "Initial production-ready Sainte-Lague web app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

