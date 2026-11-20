# run_app.py
"""
Unified server entry point for VidyaLoan cloud deployment.
Runs the Streamlit interactive UI at / while serving all FastAPI routes:
- /: Interactive Streamlit UI (Chat, Loan Cost Stacked Bar Chart, Citations, Approval)
- /health: Public health check returning {"status": "ok", "records": 59}
- /docs: Swagger API documentation
- /ask, /agent, /search/semantic, /records: All FastAPI endpoints
"""
import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Mount FastAPI routes onto Streamlit's Starlette server
try:
    import streamlit.web.server.starlette.starlette_routes as sr

    from app.main import app as fastapi_app

    orig_create_health = sr.create_health_routes

    def custom_health_routes(runtime, base_url):
        routes = orig_create_health(runtime, base_url)
        # Mount all FastAPI routes (except root which belongs to Streamlit)
        for r in fastapi_app.routes:
            path = getattr(r, "path", "")
            if path and path not in ("/", ""):
                routes.insert(0, r)
        return routes

    sr.create_health_routes = custom_health_routes
except Exception as e:
    print(f"Warning: could not mount FastAPI routes on Streamlit: {e}")

# Launch Streamlit
if __name__ == "__main__":
    from streamlit.web import cli

    port = os.getenv("PORT", "8501")
    sys.argv = [
        "streamlit",
        "run",
        "ui/app.py",
        "--server.port",
        str(port),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",
    ]
    cli.main()
