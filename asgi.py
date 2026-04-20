"""
Point d'entrée ASGI (Uvicorn) — le dashboard Dash reste dans `app.py` à la racine.

Usage :
    uvicorn asgi:app --reload --host 127.0.0.1 --port 8000

Lancement classique (Dash seul) :
    python app.py
"""

from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

# Serveur WSGI Flask généré par Dash (`app.py` à la racine)
from app import server as dash_wsgi_app

app = FastAPI(title="Dashboard Hospitalier", version="1.0.0")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hospital-dash-viz"}


app.mount("/", WSGIMiddleware(dash_wsgi_app))
