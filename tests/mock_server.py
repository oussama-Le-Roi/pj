#!/usr/bin/env python3
"""
Local mock of the Telegram Bot API + Groq/OpenRouter/Gemini endpoints.

Lets the whole bot be exercised end-to-end without any network access.
Records every outgoing call so tests can assert on them.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

STATE = {
    "sent": [],        # sendMessage payloads
    "edits": [],       # editMessageText payloads
    "callbacks": [],   # answerCallbackQuery payloads
    "actions": [],     # sendChatAction payloads
    "queue": [],       # updates handed to getUpdates
    "offsets": [],     # offsets the bot acknowledged
    "ai_calls": [],    # (provider, model) tuples
    "fail": set(),     # provider names that should return an error
    "getme_ok": True,
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # keep test output clean

    def _json(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or "{}")
        path = self.path

        # ── Telegram ──
        if "/getMe" in path:
            if not STATE["getme_ok"]:
                return self._json(404, {"ok": False, "error_code": 404,
                                        "description": "Not Found"})
            return self._json(200, {"ok": True, "result": {"id": 1, "username": "test_bot"}})

        if "/getUpdates" in path:
            if "offset" in payload:
                STATE["offsets"].append(payload["offset"])
                STATE["queue"].clear()
                return self._json(200, {"ok": True, "result": []})
            updates = list(STATE["queue"])
            return self._json(200, {"ok": True, "result": updates})

        if "/sendMessage" in path:
            STATE["sent"].append(payload)
            return self._json(200, {"ok": True, "result": {"message_id": len(STATE["sent"])}})

        if "/editMessageText" in path:
            STATE["edits"].append(payload)
            return self._json(200, {"ok": True, "result": {}})

        if "/answerCallbackQuery" in path:
            STATE["callbacks"].append(payload)
            return self._json(200, {"ok": True, "result": True})

        if "/sendChatAction" in path:
            STATE["actions"].append(payload)
            return self._json(200, {"ok": True, "result": True})

        # ── AI providers ──
        if "/groq/" in path or "/openrouter/" in path:
            provider = "groq" if "/groq/" in path else "openrouter"
            model = payload.get("model", "?")
            STATE["ai_calls"].append((provider, model))
            if provider in STATE["fail"]:
                return self._json(429, {"error": {"message": "quota exceeded"}})
            return self._json(200, {
                "choices": [{"message": {"content": f"reply from {provider}/{model}"}}]
            })

        if "generateContent" in path:
            model = path.split("/models/")[-1].split(":")[0]
            STATE["ai_calls"].append(("gemini", model))
            if "gemini" in STATE["fail"]:
                return self._json(429, {"error": {"message": "quota"}})
            return self._json(200, {
                "candidates": [{"content": {"parts": [{"text": f"reply from gemini/{model}"}]}}]
            })

        return self._json(404, {"ok": False, "description": "unknown endpoint"})


def start():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}"


def reset():
    for key in ("sent", "edits", "callbacks", "actions", "queue", "offsets", "ai_calls"):
        STATE[key].clear()
    STATE["fail"] = set()
    STATE["getme_ok"] = True
