"""
Point d'entrée WSGI pour Gunicorn / uWSGI.

À utiliser avec :
    gunicorn wsgi:application --bind 0.0.0.0:$PORT

Évite la confusion avec ``app:app`` (objet Dash, pas un WSGI Flask).
"""

from app import server as application
