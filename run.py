#!/usr/bin/env python3
"""Start the web UI. Usage: python run.py [--port N] [--host H] [--no-browser]"""
import argparse, socket, sys, threading, time, webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
DEFAULT_PORT = 8765


def free_port(start: int) -> int:
    for p in range(start, start + 40):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--host", default="127.0.0.1",
                    help="use 0.0.0.0 to reach it from another machine")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--reload", action="store_true")
    a = ap.parse_args()

    port = free_port(a.port or DEFAULT_PORT)
    url = f"http://localhost:{port}"
    print(f"\n  audiogen  ->  {url}\n  API docs  ->  {url}/api/docs\n  (Ctrl+C to stop)\n")

    from audiogen.service import health
    h = health()
    if h["problem"]:
        print(f"  warning  {h['problem']}\n")
    if not a.no_browser:
        threading.Thread(target=lambda: (time.sleep(1.2), webbrowser.open(url)),
                         daemon=True).start()
    import uvicorn
    uvicorn.run("audiogen.server:app", host=a.host, port=port,
                reload=a.reload, log_level="warning")


if __name__ == "__main__":
    main()
