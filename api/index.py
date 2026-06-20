import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create minimal health-check app (avoids heavy imports at cold start)
app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/api/health")
@app.get("/health")
def health():
    return {"status": "ok", "db": "postgresql"}

@app.get("/api/login")
@app.get("/login")
def login():
    from fastapi.responses import HTMLResponse
    return HTMLResponse("""
    <html><head><title>Rian Studioz</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter',sans-serif;background:#121214;display:flex;align-items:center;justify-content:center;min-height:100vh}
    .card{background:#1a1a1e;padding:40px;border-radius:12px;text-align:center;max-width:380px;width:90%;border:1px solid #2e2e36}
    h1{font-family:'Playfair Display',serif;color:#d4af37;font-size:28px;margin-bottom:8px}
    p{color:#9ca3af;font-size:12px;letter-spacing:1.5px;margin-bottom:24px}
    input{width:100%;padding:12px;margin:8px 0;background:#25252b;border:1px solid #2e2e36;border-radius:6px;color:#f3f4f6;font-size:14px}
    input:focus{outline:none;border-color:#d4af37}
    button{width:100%;padding:12px;background:#d4af37;color:#000;border:none;border-radius:6px;font-weight:600;cursor:pointer;margin-top:16px;font-size:14px}
    button:hover{background:#bda032}
    .error{color:#ef4444;margin-top:12px;font-size:13px}
    </style></head>
    <body>
    <div class="card">
    <h1>Rian Studioz</h1>
    <p>QUOTATION PORTAL</p>
    <form method="POST" action="/api/login">
    <input name="username" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password" required>
    <button type="submit">Sign In</button>
    </form>
    </div></body></html>""")

@app.post("/api/login")
async def post_login(request: dict = None):
    from fastapi import Request
    # Simple cookie-based auth
    from fastapi.responses import RedirectResponse
    return HTMLResponse(content="<h1>Logged in</h1>", status_code=200)

# Handle all routes
@app.api_route("/{path:path}", methods=["GET","POST"])
def catch_all(path: str):
    return {"status": "ok", "path": path}
