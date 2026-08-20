import json
import os
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "http://127.0.0.1:8000")
MAX_BODY_BYTES = 64 * 1024

SYSTEM_PROMPT = """You extract household expense transactions from natural language. Return JSON only with this shape:
{"expenses":[{"description":"string","amount":0,"date":"YYYY-MM-DD","category":"Fuel|Food|Snacks|Outing|Rent|Reimbursement|Others","payer":"string","participants":["string"],"split_type":"equal|exact|percentage","shares":{"Person":0}}],"notes":["string"]}
Rules: amount is a positive number. Use today's date if no date is given. Categorize every expense as exactly one of Fuel, Food, Snacks, Outing, Rent, Reimbursement, or Others. Use Reimbursement for repayments, paybacks, settlements, or money returned between household members. Use the closest category based on the description; use Others when uncertain. Use split_type equal when the text says equally or does not specify a different split. For exact, shares contains currency amounts. For percentage, shares contains percentages. Never invent people; use the supplied household list when possible. Put uncertainty or missing details in notes and still provide the best suggestion."""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self.respond(200, {"ok": True, "service": "split-calculator-api"})
            return
        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self.add_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/parse-expenses":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self.respond(413, {"error": "Request body is missing or too large."})
                return
            body = json.loads(self.rfile.read(length) or b"{}")
            text = str(body.get("text", "")).strip()
            people = body.get("people", [])
            if not text:
                self.respond(400, {"error": "Paste some expense text first."})
                return
            api_key = os.environ.get("LLM_API_KEY")
            if not api_key or api_key == "replace-with-your-api-key":
                self.respond(503, {"error": "LLM_API_KEY is not configured. Set it before starting the server."})
                return
            endpoint = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
            if endpoint.rstrip("/").endswith("/v1"):
                endpoint = endpoint.rstrip("/") + "/chat/completions"
            model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
            request_body = {
                "model": model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps({"household": people, "today": __import__("datetime").date.today().isoformat(), "text": text})},
                ],
            }
            request = urllib.request.Request(endpoint, data=json.dumps(request_body).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"}, method="POST")
            with urllib.request.urlopen(request, timeout=60) as response:
                provider = json.loads(response.read())
            content = provider["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            self.respond(200, parsed)
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")
            self.respond(error.code, {"error": f"Model provider error: {detail[:300]}"})
        except Exception as error:
            print(f"parse-expenses error: {error}")
            self.respond(500, {"error": "Could not parse the expenses."})

    def respond(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.add_cors_headers()
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def add_cors_headers(self):
        request_origin = self.headers.get("Origin")
        if ALLOWED_ORIGIN == "*":
            self.send_header("Access-Control-Allow-Origin", "*")
        elif request_origin and request_origin == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", request_origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

if __name__ == "__main__":
    print(f"Split calculator running at http://127.0.0.1:{PORT}/")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
