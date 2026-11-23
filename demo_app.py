"""
One-command interactive web demo for Enterprise Ops RAG Agent & Deterministic Tool-Calling.
Run: python demo_app.py
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.agent import EnterpriseOpsAgent

PORT = int(os.environ.get("PORT", "8004"))
AGENT = EnterpriseOpsAgent()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Enterprise Ops RAG Agent — Live Demo</title>
  <style>
    :root { --bg:#080e1a; --card:#111a2c; --surf:#0c1322; --bdr:#22304a; --txt:#f1f5f9; --mut:#94a3b8; --acc:#22d3ee; --grn:#10b981; --amb:#f59e0b; }
    * { box-sizing:border-box; font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",sans-serif; }
    body { margin:0; background:var(--bg); color:var(--txt); padding:24px; line-height:1.45; }
    .wrap { max-width:1200px; margin:0 auto; }
    header { display:flex; justify-content:space-between; align-items:center; padding-bottom:16px; margin-bottom:20px; border-bottom:1px solid var(--bdr); }
    h1 { margin:0; font-size:1.35rem; }
    .sub { margin:3px 0 0; font-size:0.84rem; color:var(--mut); }
    .pill { padding:5px 11px; border-radius:999px; font-size:0.75rem; font-weight:600; background:rgba(34,211,238,0.14); color:var(--acc); border:1px solid rgba(34,211,238,0.3); }
    .prompt-bar { display:flex; gap:10px; margin-bottom:16px; }
    input { flex:1; padding:11px 14px; border-radius:8px; border:1px solid var(--bdr); background:var(--card); color:var(--txt); font-size:0.92rem; }
    button { padding:10px 18px; border:none; border-radius:8px; background:var(--acc); color:#083344; font-weight:700; cursor:pointer; }
    .grid { display:grid; grid-template-columns:1.25fr 0.75fr; gap:18px; }
    .card { background:var(--card); border:1px solid var(--bdr); border-radius:10px; padding:18px; margin-bottom:16px; }
    .card h2 { margin:0 0 12px; font-size:0.86rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--mut); border-bottom:1px solid var(--bdr); padding-bottom:8px; }
    .resp { white-space:pre-wrap; font-size:0.9rem; line-height:1.6; background:var(--surf); padding:14px; border-radius:8px; border:1px solid var(--bdr); }
    .badge { display:inline-block; padding:3px 8px; border-radius:4px; font-size:0.73rem; font-weight:700; margin-right:6px; margin-bottom:6px; }
    .ok { background:rgba(16,185,129,0.16); color:var(--grn); }
    .tool { background:rgba(34,211,238,0.14); color:var(--acc); font-family:ui-monospace,monospace; }
    .cite { padding:10px; border-radius:6px; background:var(--surf); border:1px solid var(--bdr); margin-bottom:8px; font-size:0.82rem; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>Enterprise Ops RAG Agent &amp; Deterministic Tool-Calling</h1>
        <p class="sub">Hybrid Retrieval (BM25 + Dense Cosine + RRF), Pydantic v2 Tool Execution &amp; Post-Generation Numerical Grounding</p>
      </div>
      <span class="pill">FastAPI / Python · Hybrid RAG · Synthetic KB</span>
    </header>
    <div class="prompt-bar">
      <input id="q" value="Check available stock for Ferro-Manganese and review moisture deduction policy" />
      <button onclick="ask()">Execute Grounded Query</button>
    </div>
    <div class="grid">
      <div class="card">
        <h2>Grounded Agent Response</h2>
        <div id="verifyBar" style="margin-bottom:10px;"></div>
        <div class="resp" id="respBox">Loading...</div>
      </div>
      <div>
        <div class="card">
          <h2>Deterministic Tools Invoked</h2>
          <div id="toolsBox"></div>
        </div>
        <div class="card">
          <h2>Hybrid RAG Citations (BM25 + RRF)</h2>
          <div id="citesBox"></div>
        </div>
      </div>
    </div>
  </div>
  <script>
    async function ask() {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ query: document.getElementById("q").value })
      });
      const d = await res.json();
      document.getElementById("verifyBar").innerHTML =
        `<span class="badge ok">NUMERICAL GROUNDING: ${d.verified_numerical_claim ? "VERIFIED" : "UNVERIFIED"}</span>` +
        `<span class="badge tool">TOOLS: ${d.tools_invoked.length}</span>` +
        `<span class="badge tool">CITATIONS: ${d.citations.length}</span>`;
      document.getElementById("respBox").textContent = d.response_text;
      document.getElementById("toolsBox").innerHTML = d.tools_invoked.length
        ? d.tools_invoked.map(t => `<div class="cite"><code>${t}</code></div>`).join("")
        : "<span style='color:var(--mut)'>No tools invoked</span>";
      document.getElementById("citesBox").innerHTML = d.citations.length
        ? d.citations.map(c => `<div class="cite"><strong>${c.source_title}</strong><br><small style="color:var(--mut)">Score: ${Number(c.relevance_score||0).toFixed(3)}</small><div style="margin-top:4px">${c.snippet}</div></div>`).join("")
        : "<span style='color:var(--mut)'>No citations</span>";
    }
    ask();
  </script>
</body>
</html>"""


class DemoHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/query":
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            resp = AGENT.handle_query(body.get("query", ""))
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp.model_dump(), default=str).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    print(f"Enterprise Ops RAG Agent Demo running at http://127.0.0.1:{PORT}")
    HTTPServer(("127.0.0.1", PORT), DemoHandler).serve_forever()
