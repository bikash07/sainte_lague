# Nepal Election Dashboard (PR + FPTP)

Production-ready Flask web app that:
- Fetches PR vote counts from Election Commission Nepal (`PRVoteChartResult2082.aspx`).
- Computes House of Representatives PR seat allocation using Sainte-Lague.
- Fetches FPTP party result standings (`FPTPWLChartResult2082.aspx`).
- Shows both PR and FPTP data in a tabbed dashboard with tables and pie charts.

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
|   |-- static/js/main.js
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

`GET /api/fptp`

`GET /api/dashboard?seats=110&threshold=3`

`GET /healthz`

## CLI (optional)

```bash
python sainte_lague_nepal.py --seats 110 --threshold 3
```

## Deploy free on Render

1. Push this repo to GitHub.
2. In Render, create a **Web Service** (or use Blueprint from `render.yaml`).
3. Ensure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`
4. Deploy and open the service URL.
5. On each push to `main`, Render redeploys (`autoDeploy: true`).

### Render troubleshooting

- If you see **Not Found** immediately after deploy, verify the service type is **Web Service**, not Static Site.
- Check `healthCheckPath` in [render.yaml](render.yaml), currently set to `/healthz`.
- Use Render runtime logs to confirm Gunicorn started and Flask routes are mounted.

## CI

GitHub Actions workflow is included at `.github/workflows/ci.yml`.
- Triggers on push and pull request to `main`
- Tests on Python 3.11 and 3.12
- Installs dependencies and runs `pytest -q`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

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

## Line endings

This repo includes `.gitattributes` to keep source files consistent with LF endings across platforms.
