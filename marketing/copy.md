# Unstop MCP — Marketing & Monetization Kit

---

## 1. Product Hunt Launch

**Name:** Unstop MCP Server

**Tagline:**
> Search 2,500+ Unstop opportunities directly from Claude — no tab switching

**Description:**
I built an open-source MCP server that connects Claude to Unstop's live catalog of competitions, hackathons, jobs, internships, and scholarships.

12 tools. 5 opportunity types. Zero API keys. Works with Claude Desktop, Claude.ai, and Claude Code.

**What you can do:**
- "Find AI hackathons closing this week with a ₹50k+ prize"
- "Show me remote Python jobs on Unstop"
- "What competitions are open right now?"
- "Get full details for the Smart India Hackathon"
- "Find paid internships paying at least ₹20,000/month"

**Why I built it:** I was tired of switching to Unstop every time I wanted to check what was open. MCP lets Claude pull live data, so now I just ask.

**Deploy free in one click on Render** — then add it to Claude.ai as a remote connector via Settings → Integrations.

👉 GitHub: https://github.com/janmejai2002/unstop-mcp
👉 Landing page: https://janmejai2002.github.io/unstop-mcp/

**First comment (maker post):**
Hey PH! 👋

This started as a weekend project — I kept tab-switching between Claude and Unstop to find hackathons. Took me a day to reverse-engineer Unstop's public API and wrap it in 12 MCP tools.

A few things I learned:
- Unstop's API is rich but undocumented — had to discover it by watching network requests
- `find_closing_soon` has become my most-used tool — never miss a deadline again
- The `find_by_prize` tool sorted by cash prize was a surprise hit

No API key needed, MIT licensed, runs in 60 seconds. Happy to answer questions!

---

## 2. Twitter / X Thread

**Tweet 1 (hook):**
I got tired of switching tabs to check Unstop every time I was in Claude.

So I built an MCP server that brings all of Unstop into Claude.

12 tools. Zero API keys. Free.

Here's what it can do 🧵

---

**Tweet 2:**
"Find AI hackathons closing this week with a ₹50k+ prize"

Claude searches Unstop live, returns the top results with prizes, deadlines, and registration links.

No copy-pasting. No tab switching.

---

**Tweet 3:**
The tools it gives Claude:

🏆 search_competitions
💻 search_hackathons
💼 search_jobs (with salary/remote filter)
🎓 search_internships (with stipend filter)
📚 search_scholarships
💰 find_by_prize — sorted by cash, highest first
⏰ find_closing_soon — sorted by deadline

---

**Tweet 4:**
Real example:

Me: "Find paid internships with ₹20k+ stipend"

Claude: Found 5 — AI Summer Internship (₹20k/mo), Business Strategist (₹20k–₹30k), Backend Dev (₹15k–₹20k)...

All from Unstop's live API. Fresh data every time.

---

**Tweet 5:**
Works with:
→ Claude Desktop (local stdio)
→ Claude.ai (remote SSE connector)
→ Claude Code CLI
→ Any MCP-compatible app

---

**Tweet 6:**
Setup in 60 seconds:

```
git clone github.com/janmejai2002/unstop-mcp
pip install -r requirements.txt
```

Add to claude_desktop_config.json and restart.

Or deploy free on Render and add as a Claude.ai connector →

---

**Tweet 7:**
The `find_closing_soon` tool is my favourite.

Set days=3 and Claude shows you every competition/hackathon closing in the next 3 days, sorted by urgency.

Never miss a registration deadline again.

---

**Tweet 8:**
For hackathons specifically, `find_by_prize` scans the page and returns only those above your minimum — sorted highest cash first.

Useful if you only care about competitions that actually pay.

---

**Tweet 9:**
The whole thing is built on FastMCP + httpx.

Took ~6 hours to:
- Reverse-engineer Unstop's undocumented API
- Design 12 coherent tools
- Add client-side salary/stipend filtering
- Deploy and test against live data

---

**Tweet 10 (CTA):**
It's fully open source under MIT.

⭐ Star it → github.com/janmejai2002/unstop-mcp
🚀 Deploy free → one-click Render button in the README
🌐 Landing page → janmejai2002.github.io/unstop-mcp/

If you use Unstop for hackathons or job hunting, this saves real time. RT if useful!

---

## 3. LinkedIn Post

**Title:** I built an MCP server that brings Unstop into Claude — here's what it does

As someone who uses both Claude and Unstop regularly, I got tired of the constant tab-switching.

So I spent a weekend building an open-source MCP (Model Context Protocol) server that connects Claude directly to Unstop's live catalog.

**What it enables:**

Instead of going to Unstop, searching, filtering, opening listings — you just ask Claude:
- "Find AI hackathons closing this week with a cash prize"
- "Show me remote jobs on Unstop paying ₹30k+"
- "Get full details for the Smart India Hackathon"
- "Which competitions close in the next 3 days?"

Claude calls the right tools, fetches live data, and returns clean, structured results — complete with prizes, deadlines, eligibility, and apply links.

**Technical details:**
- 12 MCP tools covering competitions, hackathons, jobs, internships, and scholarships
- Reverse-engineered Unstop's public API (no official docs exist)
- Works with Claude Desktop, Claude.ai, and Claude Code CLI
- Deploy free on Render in one click

**Learnings from building it:**
1. Unstop's API is undocumented but rich — took ~2 hours to reverse-engineer from network traffic
2. Client-side salary/stipend filtering was necessary because the API doesn't support it
3. Title-similarity scoring (difflib) was needed because the search API doesn't guarantee the best match is first
4. The MCP SSE transport needs to be on a public HTTPS URL for Claude.ai connector registration

Open source, MIT licensed, free to use and deploy.

GitHub: https://github.com/janmejai2002/unstop-mcp

Happy to answer questions about MCP servers, FastMCP, or the reverse engineering process.

#MCP #Claude #AI #Unstop #OpenSource #Python #Hackathon

---

## 4. Dev.to / Hashnode Article

**Title:** How I built an MCP server for Unstop in one day (reverse engineering + 12 tools)

**Tags:** #mcp #python #ai #opensource #claude

**Intro:**
I wanted to search Unstop without leaving Claude. There was no official MCP server for it, so I built one. This post covers everything: reverse engineering the API, designing the tools, handling edge cases, and deploying it for free.

**Sections:**

### What is MCP?
(Brief explanation — Model Context Protocol, how it lets Claude use external tools)

### Why Unstop?
Unstop has 2,500+ live opportunities but no public API docs. Every student in India uses it for hackathons and job hunting.

### Step 1: Reverse Engineering the API
- Open DevTools → Network tab → search competitions
- Found: `https://unstop.com/api/public/opportunity/search-result`
- No auth required — just a browser User-Agent header
- Parameters: `opportunity`, `oppstatus`, `per_page`, `page`, `searchTerm`, `region`
- Types: competitions, hackathons, jobs, internships, scholarships

### Step 2: Designing the 12 Tools
- What are the natural user queries?
- Type-specific tools vs universal search
- Client-side filters for salary/stipend (API doesn't support them)
- `find_closing_soon` — the most useful one
- `find_by_prize` — filters + sorts by cash prize

### Step 3: Edge Cases
- Title-similarity scoring with difflib (search API doesn't guarantee best match first)
- HTML stripping from the `details` field
- Currency symbols (₹, $, €)
- UTF-8 on Windows (cp1252 issues)

### Step 4: Two Transports
- stdio for Claude Desktop/Code
- SSE for remote Claude.ai connector

### Step 5: Free Deployment on Render
- render.yaml for one-click deploy
- `/sse` health check endpoint
- Free tier limitations (15 min sleep)

### Results
- All 12 tools working against live API
- Full MCP handshake verified
- 2,500+ opportunities accessible from Claude

**Code snippets:** show the key parts of server.py, _best_match, _job_detail

**GitHub link + landing page**

---

## 5. Reddit Posts

### r/india
**Title:** Built a free tool that lets Claude search Unstop for you — competitions, hackathons, jobs, internships

**Body:**
Hey r/india,

Made something that might be useful for students and job hunters here.

I built an MCP (Model Context Protocol) server that connects Claude AI to Unstop's live catalog. Instead of going to Unstop, searching, filtering, clicking around — you just ask Claude:

- "Find hackathons closing this week with cash prizes"
- "Show me remote jobs paying ₹30k+"
- "Which competitions are open for engineering students?"

It fetches live data from Unstop in real time. Works with Claude Desktop (free) and Claude.ai.

12 tools covering competitions, hackathons, jobs, internships, scholarships. No API key needed, MIT licensed.

GitHub: https://github.com/janmejai2002/unstop-mcp

Has anyone else been using Claude + Unstop? What other integrations would be useful?

---

### r/ClaudeAI
**Title:** I built an MCP server for Unstop (competitions, hackathons, jobs, internships) — open source

**Body:**
Built an open-source MCP server that connects Claude to Unstop's live opportunity catalog.

12 tools:
- search_competitions, search_hackathons, search_jobs, search_internships, search_scholarships
- find_by_prize (filter by minimum cash prize, sorted highest first)
- find_closing_soon (deadlines within N days, sorted soonest)
- get_opportunity_details (full record with eligibility, skills, team size, apply link)
- get_platform_stats (live counts for all types)

Works with Claude Desktop (stdio) and Claude.ai (SSE remote connector). Deploy free on Render.

GitHub: https://github.com/janmejai2002/unstop-mcp

Happy to explain how I reverse-engineered Unstop's undocumented API or how the MCP SSE transport works for remote connectors.

---

### r/learnprogramming
**Title:** How I built my first MCP server — reverse engineering an undocumented API + 12 tools in Python

**Body:**
Weekend project writeup: I built an MCP server for Unstop (India's biggest student opportunity platform) that gives Claude live access to competitions, hackathons, jobs, and internships.

**What I learned:**
1. How to reverse-engineer a JSON API using browser DevTools
2. FastMCP — Python library for building MCP servers in minutes
3. Two MCP transports: stdio (local) and SSE (HTTP, for remote connectors)
4. difflib.SequenceMatcher for fuzzy title matching
5. Handling UTF-8 vs cp1252 on Windows

Source: https://github.com/janmejai2002/unstop-mcp

If you want to build your own MCP server for any API, this is a good starter template.

---

## 6. Discord / Community Post

**For: Unstop Discord / College tech communities**

Hey everyone! 👋

Just dropped something that might save you time on Unstop.

**Unstop MCP** — a tool that lets you search all of Unstop from inside Claude AI, without opening a browser.

Examples:
→ "Find hackathons closing this week"
→ "Which competitions have prizes over ₹50,000?"
→ "Show me remote internships with ₹20k+ stipend"

Free to use, open source.

Setup: https://github.com/janmejai2002/unstop-mcp
Landing page: https://janmejai2002.github.io/unstop-mcp/

Let me know if you have feature requests!

---

## 7. Monetization Strategy

### Phase 1 — Audience Building (Month 1-2)
**Goal:** 100+ GitHub stars, active users

Actions:
- Post on all platforms above on launch day
- Submit to MCP directories (mcp.so, glama.ai/mcp)
- Submit to awesome-mcp-servers list on GitHub
- Post in Claude Discord server
- Add Buy Me a Coffee / GitHub Sponsors link

Revenue: $0 (intentionally free, building reputation)

---

### Phase 2 — Premium Hosted Tier (Month 3-4)
**Goal:** First paying users

**What to build:**
- Auth layer (API key) on the hosted version
- Rate limiting on free tier (100 calls/day)
- Usage dashboard (simple)
- Stripe payment integration

**Pricing:**
| Tier | Price | Limits |
|---|---|---|
| Free | ₹0 | 100 calls/day, may sleep |
| Pro | ₹499/mo (~$6) | Unlimited, always-on |
| Teams | ₹1499/mo (~$18) | 5 seats, priority |

**Revenue target:** 20 Pro users = ₹10,000/mo

---

### Phase 3 — Alert System (Month 4-6)
**Goal:** Recurring value, lower churn

**Features:**
- Email alerts: "Notify me when new AI hackathons open"
- Webhook support: send to Slack, Discord, custom URL
- Saved filters: "Competitions · Online · Engineering students · Prize > ₹25k"
- Weekly digest: "Here are 10 open opportunities matching your profile"

**How to build:**
- Cron job polling the Unstop API every 30 min
- User preference storage (Supabase free tier)
- Email via Resend / SendGrid free tier

**Pricing:**
- Free tier: no alerts
- Pro: 3 alert rules
- Teams: unlimited alert rules + team inbox

---

### Phase 4 — API Product (Month 6+)
**Goal:** Developer revenue

**Offer:**
A rate-limited JSON API over the same Unstop data, with:
- API key auth
- Swagger docs
- Webhooks
- SDKs (Python, JS)

Priced per call or per seat for startups building on top.

**Target customers:**
- EdTech startups that want to surface Unstop data in their apps
- College portals wanting opportunity recommendations
- Career coaching apps

---

### Phase 5 — Claude Connector Marketplace (Future)
When Anthropic opens a paid connector marketplace:
- List as a verified connector
- Revenue share model from Anthropic
- Premium connector features (featured placement, etc.)

---

### Quick Wins (Start Now — ₹0 cost)
1. Add GitHub Sponsors button to the repo
2. Add "Buy Me a Coffee" link to README and landing page
3. Submit to: mcp.so, glama.ai/mcp/servers, github.com/punkpeye/awesome-mcp-servers
4. Ask for GitHub stars in every post
5. Make a 60-second demo video showing a real Claude conversation

---

### KPIs to Track
- GitHub stars (target: 100 in month 1, 500 in month 3)
- Render deployments (track via Render dashboard)
- Unique visitors to landing page (GitHub Pages analytics via GoatCounter — free)
- Discord mentions / community reposts
- Email signups (add a simple waitlist form to the landing page)
