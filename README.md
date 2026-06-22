# ⚡ Unstop MCP

> Search competitions, hackathons, jobs, internships & scholarships on [Unstop](https://unstop.com) **directly from Claude** — no browser tab switching needed.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/janmejai2002/unstop-mcp)
&nbsp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)

**12 tools · 5 opportunity types · 2,500+ live listings · zero API keys required**

🌐 **Landing page:** https://janmejai2002.github.io/unstop-mcp/

---

## Tools

| Tool | Description |
|---|---|
| `get_platform_stats` | Live counts for all 5 opportunity types |
| `search_opportunities` | Universal search across any type |
| `search_competitions` | Case studies, quizzes, essay contests |
| `search_hackathons` | Coding & innovation hackathons with region filter |
| `search_jobs` | Jobs with remote/salary/timing filters |
| `search_internships` | Internships with WFH and stipend filters |
| `search_scholarships` | Scholarships and fellowships |
| `get_opportunity_details` | Full record: prizes, dates, eligibility, skills, apply link |
| `get_competition_details` | Shorthand details for competitions |
| `find_by_prize` | Filter by minimum cash prize, sorted highest first |
| `find_closing_soon` | Deadlines within N days, sorted soonest first |
| `list_open_competitions` | Quick "what's open right now" |

---

## Quick start

```bash
git clone https://github.com/janmejai2002/unstop-mcp.git
cd unstop-mcp
python -m venv .venv

# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe smoke_test.py

# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
python smoke_test.py
```

---

## Connect to Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or  
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "unstop": {
      "command": "C:\\path\\to\\unstop-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\unstop-mcp\\server.py"]
    }
  }
}
```

Restart Claude Desktop. The 🔌 menu now shows all 12 Unstop tools.

## Connect to Claude Code (CLI)

```bash
claude mcp add unstop -- /path/to/.venv/Scripts/python.exe /path/to/server.py
```

---

## Deploy free on Render ← one click

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/janmejai2002/unstop-mcp)

This gives you a public `https://unstop-mcp.onrender.com` URL.

**Manual steps if you prefer:**
1. Fork this repo on GitHub
2. [render.com](https://render.com) → New Web Service → connect your fork
3. Build command: `pip install -r requirements.txt`
4. Start command: `python server.py --transport sse --host 0.0.0.0 --port $PORT`
5. Your SSE endpoint: `https://your-service.onrender.com/sse`

> Free tier sleeps after 15 min of inactivity and wakes in ~30 s on the next request. Acceptable for a personal connector.

---

## Add as a Claude.ai Remote Connector

1. Deploy on Render (above) to get your public HTTPS URL
2. **Claude.ai → Settings → Integrations → Add custom integration**
3. Paste `https://your-service.onrender.com/sse`
4. Name it **Unstop** → click Add
5. All 12 tools now appear in every Claude.ai conversation

### Test locally with ngrok (instant)

```bash
# Terminal 1 — start SSE server
python server.py --transport sse --port 8000

# Terminal 2 — expose via ngrok
ngrok http 8000
# Paste https://xxxx.ngrok-free.app/sse into Claude.ai integrations
```

---

## Example prompts

```
What hackathons are open on Unstop right now?
Find AI competitions with a prize pool over ₹1 lakh.
Show me remote Python developer jobs on Unstop.
Which Unstop competitions close in the next 3 days?
Give me full details for the Smart India Hackathon.
Find paid internships with at least ₹20,000/month stipend.
How many jobs vs internships are open on Unstop today?
Search for blockchain hackathons online.
```

---

## Enable GitHub Pages (landing page)

1. Repo → **Settings → Pages**
2. Source: **Deploy from a branch** → branch `main`, folder `/docs`
3. Click Save — live in ~60 s at `https://janmejai2002.github.io/unstop-mcp/`

---

## License

MIT — free to use, fork, and build on.

---

*Built with [FastMCP](https://github.com/jlowin/fastmcp) · Data from [Unstop](https://unstop.com) public API · Not affiliated with Unstop*
