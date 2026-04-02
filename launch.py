"""
launch.py — Unified launcher for AI Academic Research Assistant.

Starts the FastAPI backend in a background thread, waits until it is healthy,
then launches the Gradio UI on http://127.0.0.1:7860.

Usage:
    python launch.py
"""

import sys
import time
import threading
import uvicorn
import requests

# ─── Settings ────────────────────────────────────────────────────────────────
API_HOST = "127.0.0.1"
API_PORT = 8000
GRADIO_PORT = 7860
HEALTH_URL = f"http://{API_HOST}:{API_PORT}/health"
HEALTH_RETRIES = 30       # seconds to wait for backend
HEALTH_INTERVAL = 1.0     # seconds between retries


# ─── Backend thread ───────────────────────────────────────────────────────────

def run_backend():
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )


def wait_for_backend() -> bool:
    print(f"[*] Waiting for FastAPI backend on {HEALTH_URL} ...")
    for attempt in range(HEALTH_RETRIES):
        try:
            r = requests.get(HEALTH_URL, timeout=3)
            if r.status_code == 200 and r.json().get("status") == "ok":
                print("[OK] Backend is healthy.")
                return True
        except Exception:
            pass
        time.sleep(HEALTH_INTERVAL)
        print(f"   retry {attempt + 1}/{HEALTH_RETRIES} ...")
    return False


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    # Start backend thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Wait for it to be healthy
    if not wait_for_backend():
        print("[ERROR] Backend failed to start. Check logs above and your .env config.")
        sys.exit(1)

    # Import and launch Gradio (must happen after backend starts so env is loaded)
    from app.frontend.gradio_ui import demo, THEME, CSS

    print(f"\n[>>] Launching Gradio UI at http://127.0.0.1:{GRADIO_PORT}\n")
    demo.launch(server_name="127.0.0.1", server_port=GRADIO_PORT, share=True, theme=THEME, css=CSS)


if __name__ == "__main__":
    main()
