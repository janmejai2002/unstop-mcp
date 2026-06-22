"""Unstop MCP Server

Exposes the full Unstop platform — competitions, hackathons, jobs, internships,
and scholarships — to MCP clients (Claude Desktop, Claude Code, etc.) via
Unstop's public, unauthenticated search API:

    https://unstop.com/api/public/opportunity/search-result

No API key required. Run with: python server.py
For HTTP/SSE (remote connector) mode: python server.py --transport sse --port 8000
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

def _make_mcp(host: str = "127.0.0.1", port: int = 8000) -> FastMCP:
    return FastMCP(
        "unstop",
        instructions=(
            "This server lets you browse, search, and explore every opportunity on Unstop "
            "(https://unstop.com) — competitions, hackathons, jobs, internships, and scholarships. "
            "Start with `get_platform_stats` for a quick overview, then use the type-specific "
            "search tools. All data is live from the Unstop public API."
        ),
        host=host,
        port=port,
    )

# Default instance used by the decorators below.
mcp = _make_mcp()


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: Any) -> Any:
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok"})


# ─── Constants ─────────────────────────────────────────────

API_URL = "https://unstop.com/api/public/opportunity/search-result"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://unstop.com/",
}

OPP_TYPES = {"competitions", "hackathons", "jobs", "internships", "scholarships"}
VALID_STATUS = {"open", "closed", "recent"}

_CURRENCY: dict[str, str] = {
    "fa-rupee": "₹", "fa-dollar": "$", "fa-usd": "$", "fa-euro": "€", "fa-pound": "£",
}


def _strip_html(raw: str | None, limit: int | None = None) -> str:
    if not raw:
        return ""
    text = re.sub(r"<\s*(br|/p|/li|/div|/h[1-6])\s*/?>", "\n", raw, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()
    if limit and len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def _cur(code: str | None) -> str:
    return _CURRENCY.get(code or "", "")


def _prize_summary(prizes: list[dict] | None) -> str:
    if not prizes:
        return "Not specified"
    parts: list[str] = []
    for p in prizes:
        label = (p.get("rank") or "").strip()
        cash = p.get("cash") or p.get("max_cash")
        sym = _cur(p.get("currency"))
        if cash and cash > 0:
            parts.append(f"{sym}{int(cash):,}")
        elif label:
            parts.append(label)
    seen: list[str] = []
    for x in parts:
        if x not in seen:
            seen.append(x)
    return "; ".join(seen) if seen else "Not specified"


def _total_cash(prizes: list[dict] | None) -> int:
    if not prizes:
        return 0
    return sum(int(p.get("cash") or 0) for p in prizes)


def _eligibility(filters: list[dict] | None) -> list[str]:
    if not filters:
        return []
    return [f["name"] for f in filters if f.get("type") == "eligible" and f.get("name")]


def _skills(required: list[dict] | None) -> list[str]:
    if not required:
        return []
    return [s.get("skill_name") or s.get("skill", "") for s in required if s.get("skill_name") or s.get("skill")]


def _location(item: dict) -> str:
    region = (item.get("region") or "").lower()
    locs = item.get("locations") or []
    names = [l.get("city") or l.get("name") for l in locs if isinstance(l, dict)]
    names = [n for n in names if n]
    if names:
        return ", ".join(names[:3])
    if region == "online":
        return "Online"
    return region.title() if region else "Not specified"


def _regn(item: dict) -> dict:
    rr = item.get("regnRequirements") or {}
    return {
        "opens": rr.get("start_regn_dt"),
        "closes": rr.get("end_regn_dt") or item.get("end_date"),
        "time_left": rr.get("remain_days"),
        "min_team": rr.get("min_team_size"),
        "max_team": rr.get("max_team_size"),
    }


def _job_detail(item: dict) -> dict | None:
    jd = item.get("jobDetail")
    if not jd:
        return None
    sym = _cur(jd.get("currency"))
    lo, hi = jd.get("min_salary"), jd.get("max_salary")

    def fmt_pay(v: int | None) -> str | None:
        return f"{sym}{int(v):,}" if v else None

    pay_in = jd.get("pay_in") or ""
    pay_label = {"monthly": "/month", "annually": "/year", "weekly": "/week"}.get(pay_in, f"/{pay_in}" if pay_in else "")

    salary_str: str | None = None
    if not jd.get("not_disclosed") and jd.get("show_salary"):
        if lo and hi and lo != hi:
            salary_str = f"{fmt_pay(lo)}–{fmt_pay(hi)}{pay_label}"
        elif hi:
            salary_str = f"{fmt_pay(hi)}{pay_label}"
        elif lo:
            salary_str = f"{fmt_pay(lo)}{pay_label}"

    work_type_map = {"wfh": "Remote / WFH", "in_office": "In-office", "hybrid": "Hybrid", "field": "Field"}
    timing_map = {"full_time": "Full-time", "part_time": "Part-time", "contract": "Contract", "freelance": "Freelance"}

    return {
        "salary": salary_str,
        "salary_disclosed": not jd.get("not_disclosed", True),
        "work_type": work_type_map.get(jd.get("type") or "", jd.get("type")),
        "timing": timing_map.get(jd.get("timing") or "", jd.get("timing")),
        "paid": jd.get("paid_unpaid") == "paid",
        "min_experience": jd.get("min_experience"),
        "max_experience": jd.get("max_experience"),
        "min_salary_raw": lo,
        "max_salary_raw": hi,
    }


def _workfunctions(item: dict) -> list[str]:
    wf = item.get("workfunction") or []
    return [w.get("name") for w in wf if w.get("name")]


def _url(item: dict) -> str | None:
    s = item.get("seo_url")
    if s:
        return s
    p = item.get("public_url")
    return f"https://unstop.com/{p}" if p else None


def _days_left(item: dict) -> int | None:
    rr = item.get("regnRequirements") or {}
    rt = rr.get("remaining_time")
    if rt is not None:
        return max(0, int(rt) // 86400)
    return None


def _summarize(item: dict) -> dict:
    org = item.get("organisation") or {}
    rr = _regn(item)
    base: dict[str, Any] = {
        "id": item.get("id"),
        "type": item.get("type", ""),
        "title": item.get("title"),
        "organization": org.get("name"),
        "status": item.get("status"),
        "registration_open": bool(item.get("regn_open")),
        "registration_closes": rr["closes"],
        "time_left": rr["time_left"],
        "prize": _prize_summary(item.get("prizes")),
        "location": _location(item),
        "registrations": item.get("registerCount"),
        "views": item.get("viewsCount"),
        "is_paid": bool(item.get("isPaid")),
        "url": _url(item),
        "snippet": _strip_html(item.get("details"), limit=200),
    }
    jd = _job_detail(item)
    if jd:
        base["salary"] = jd.get("salary")
        base["work_type"] = jd.get("work_type")
        base["timing"] = jd.get("timing")
    return base


def _full_detail(item: dict) -> dict:
    org = item.get("organisation") or {}
    rr = _regn(item)
    out: dict[str, Any] = {
        "id": item.get("id"),
        "type": item.get("type"),
        "subtype": item.get("subtype"),
        "title": item.get("title"),
        "organization": org.get("name"),
        "organization_url": f"https://unstop.com/{org['public_url']}" if org.get("public_url") else None,
        "status": item.get("status"),
        "registration_open": bool(item.get("regn_open")),
        "registration": rr,
        "is_paid": bool(item.get("isPaid")),
        "url": _url(item),
        "location": _location(item),
        "region": item.get("region"),
        "description": _strip_html(item.get("details")),
        "eligibility": _eligibility(item.get("filters")),
        "skills": _skills(item.get("required_skills")),
        "registrations": item.get("registerCount"),
        "views": item.get("viewsCount"),
        "prizes": [{"rank": p.get("rank"), "cash": p.get("cash"), "currency": _cur(p.get("currency")), "others": p.get("others")} for p in (item.get("prizes") or [])],
        "prize_summary": _prize_summary(item.get("prizes")),
        "total_prize_cash": _total_cash(item.get("prizes")),
        "team_size": {"min": rr["min_team"], "max": rr["max_team"]},
    }
    jd = _job_detail(item)
    if jd:
        out["job_details"] = jd
        out["work_functions"] = _workfunctions(item)
    return out


def _best_match(items: list[dict], query: str) -> dict:
    q = query.lower().strip()

    def score(it: dict) -> float:
        t = (it.get("title") or "").lower().strip()
        if not t:
            return 0.0
        if t == q:
            return 1.0
        r = SequenceMatcher(None, q, t).ratio()
        if q in t or t in q:
            r = max(r, 0.9)
        return r

    return max(items, key=score)


async def _fetch(params: dict) -> dict:
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resp = await client.get(API_URL, params=params)
        resp.raise_for_status()
        return resp.json().get("data") or {}


def _validate(opportunity_type: str, status: str) -> str | None:
    if opportunity_type not in OPP_TYPES:
        return f"Invalid type '{opportunity_type}'. Choose from: {sorted(OPP_TYPES)}."
    if status not in VALID_STATUS:
        return f"Invalid status '{status}'. Choose from: {sorted(VALID_STATUS)}."
    return None


# ─── Tools ─────────────────────────────────────────────────────

@mcp.tool()
async def get_platform_stats() -> dict:
    """Get a live snapshot of all opportunity counts on Unstop.

    Returns total open / closed counts for competitions, hackathons,
    jobs, internships, and scholarships.
    """
    result: dict[str, Any] = {"by_type": {}, "total_open": 0}
    for opp in sorted(OPP_TYPES):
        counts: dict[str, Any] = {}
        for st in ("open", "closed"):
            try:
                d = await _fetch({"opportunity": opp, "oppstatus": st, "page": 1, "per_page": 1})
                counts[st] = d.get("total", 0)
            except httpx.HTTPError as e:
                counts[st] = f"error: {e}"
        result["by_type"][opp] = counts
        result["total_open"] += counts.get("open") or 0
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


@mcp.tool()
async def search_opportunities(
    query: str = "",
    opportunity_type: str = "competitions",
    status: str = "open",
    region: str = "",
    page: int = 1,
    per_page: int = 15,
) -> dict:
    """Universal search across all Unstop opportunity types.

    Args:
        query: Free-text keywords. Leave empty to browse.
        opportunity_type: competitions | hackathons | jobs | internships | scholarships.
        status: open | closed | recent.
        region: online | offline | (empty for all).
        page: 1-based page number.
        per_page: Results per page (1-50).
    """
    opportunity_type = opportunity_type.lower().strip()
    status = status.lower().strip()
    err = _validate(opportunity_type, status)
    if err:
        return {"error": err}
    per_page = max(1, min(per_page, 50))

    params: dict[str, Any] = {
        "opportunity": opportunity_type,
        "oppstatus": status,
        "page": page,
        "per_page": per_page,
    }
    if query.strip():
        params["searchTerm"] = query.strip()
    if region.strip().lower() in ("online", "offline", "hybrid"):
        params["region"] = region.strip().lower()

    try:
        data = await _fetch(params)
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    return {
        "query": query or None, "type": opportunity_type, "status": status, "region": region or None,
        "page": data.get("current_page", page), "per_page": data.get("per_page", per_page),
        "total": data.get("total"), "total_pages": data.get("last_page"),
        "count": len(items), "results": [_summarize(it) for it in items],
    }


@mcp.tool()
async def search_competitions(query: str = "", status: str = "open", region: str = "", page: int = 1, per_page: int = 15) -> dict:
    """Search competitions on Unstop (case studies, quizzes, essay contests, coding challenges)."""
    return await search_opportunities(query=query, opportunity_type="competitions", status=status, region=region, page=page, per_page=per_page)


@mcp.tool()
async def search_hackathons(query: str = "", status: str = "open", region: str = "", page: int = 1, per_page: int = 15) -> dict:
    """Search hackathons on Unstop.

    Args:
        query: Keywords e.g. 'machine learning', 'blockchain', 'fintech'.
        status: open | closed | recent.
        region: online | offline | (empty for all).
    """
    return await search_opportunities(query=query, opportunity_type="hackathons", status=status, region=region, page=page, per_page=per_page)


@mcp.tool()
async def search_jobs(
    query: str = "",
    status: str = "open",
    work_type: str = "",
    timing: str = "",
    min_salary: int = 0,
    page: int = 1,
    per_page: int = 15,
) -> dict:
    """Search jobs on Unstop with optional work-type and salary filters.

    Args:
        query: Role or skill keywords e.g. 'python developer', 'data analyst'.
        work_type: remote | in_office | hybrid.
        timing: full_time | part_time | contract | freelance.
        min_salary: Minimum monthly salary in INR (client-side filter; 0 = off).
    """
    status = status.lower().strip()
    err = _validate("jobs", status)
    if err:
        return {"error": err}

    fetch_count = min(max(per_page, 40) if min_salary > 0 else per_page, 50)
    params: dict[str, Any] = {"opportunity": "jobs", "oppstatus": status, "page": page, "per_page": fetch_count}
    if query.strip():
        params["searchTerm"] = query.strip()

    try:
        data = await _fetch(params)
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    summarized = [_summarize(it) for it in items]

    _wt = {"remote": "wfh", "wfh": "wfh", "in_office": "in_office", "hybrid": "hybrid"}
    if work_type.strip():
        wk = _wt.get(work_type.lower().strip(), work_type.lower().strip())
        pairs = [(s, it) for s, it in zip(summarized, items) if (it.get("jobDetail") or {}).get("type", "") == wk]
        summarized, items = [s for s, _ in pairs], [it for _, it in pairs]

    if timing.strip():
        tk = timing.lower().strip()
        pairs = [(s, it) for s, it in zip(summarized, items) if (it.get("jobDetail") or {}).get("timing", "") == tk]
        summarized, items = [s for s, _ in pairs], [it for _, it in pairs]

    if min_salary > 0:
        pairs = [(s, it) for s, it in zip(summarized, items)
                 if ((it.get("jobDetail") or {}).get("max_salary") or 0) >= min_salary
                 or ((it.get("jobDetail") or {}).get("min_salary") or 0) >= min_salary]
        summarized = [s for s, _ in pairs]

    return {
        "query": query or None, "type": "jobs", "status": status,
        "filters": {"work_type": work_type or None, "timing": timing or None, "min_salary": min_salary or None},
        "page": data.get("current_page", page), "total_unfiltered": data.get("total"),
        "count": len(summarized[:per_page]), "results": summarized[:per_page],
    }


@mcp.tool()
async def search_internships(
    query: str = "",
    status: str = "open",
    work_type: str = "",
    min_stipend: int = 0,
    page: int = 1,
    per_page: int = 15,
) -> dict:
    """Search internships on Unstop with optional WFH and stipend filters.

    Args:
        query: Role or company keywords e.g. 'marketing intern', 'software development'.
        work_type: remote | wfh | in_office | hybrid.
        min_stipend: Minimum monthly stipend in INR (client-side filter; 0 = off).
    """
    status = status.lower().strip()
    err = _validate("internships", status)
    if err:
        return {"error": err}

    fetch_count = min(max(per_page, 40) if min_stipend > 0 or work_type else per_page, 50)
    params: dict[str, Any] = {"opportunity": "internships", "oppstatus": status, "page": page, "per_page": fetch_count}
    if query.strip():
        params["searchTerm"] = query.strip()

    try:
        data = await _fetch(params)
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    _wt = {"remote": "wfh", "wfh": "wfh", "in_office": "in_office", "hybrid": "hybrid"}
    if work_type.strip():
        wk = _wt.get(work_type.lower().strip(), work_type.lower().strip())
        items = [it for it in items if (it.get("jobDetail") or {}).get("type", "") == wk]
    if min_stipend > 0:
        items = [it for it in items
                 if ((it.get("jobDetail") or {}).get("max_salary") or 0) >= min_stipend
                 or ((it.get("jobDetail") or {}).get("min_salary") or 0) >= min_stipend]

    return {
        "query": query or None, "type": "internships", "status": status,
        "filters": {"work_type": work_type or None, "min_stipend": min_stipend or None},
        "page": data.get("current_page", page), "total_unfiltered": data.get("total"),
        "count": len(items[:per_page]), "results": [_summarize(it) for it in items[:per_page]],
    }


@mcp.tool()
async def search_scholarships(query: str = "", status: str = "open", page: int = 1, per_page: int = 15) -> dict:
    """Search scholarships and fellowship programs on Unstop."""
    return await search_opportunities(query=query, opportunity_type="scholarships", status=status, page=page, per_page=per_page)


@mcp.tool()
async def get_opportunity_details(query: str, opportunity_type: str = "competitions", status: str = "open") -> dict:
    """Get the full details of any Unstop opportunity by title or keywords.

    Returns the complete record: description, all prizes, team size, registration
    dates, eligibility criteria, required skills, organizer info, salary/stipend,
    and the direct apply URL.

    Args:
        query: Title or distinctive keywords to look up.
        opportunity_type: competitions | hackathons | jobs | internships | scholarships.
        status: open | closed | recent.
    """
    if not query.strip():
        return {"error": "Provide keywords or a title to look up."}
    opportunity_type = opportunity_type.lower().strip()
    status = status.lower().strip()
    err = _validate(opportunity_type, status)
    if err:
        return {"error": err}

    try:
        data = await _fetch({"opportunity": opportunity_type, "oppstatus": status, "page": 1, "per_page": 20, "searchTerm": query.strip()})
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    if not items:
        return {"error": f"No {status} {opportunity_type} found matching '{query}'.", "hint": "Try broader keywords or change status to 'recent' or 'closed'."}

    best = _best_match(items, query)
    others = [{"id": it["id"], "title": it.get("title"), "organization": (it.get("organisation") or {}).get("name")} for it in items if it is not best][:5]
    result = _full_detail(best)
    if others:
        result["other_matches"] = others
    return result


@mcp.tool()
async def get_competition_details(query: str, status: str = "open") -> dict:
    """Shorthand for get_opportunity_details scoped to competitions."""
    return await get_opportunity_details(query=query, opportunity_type="competitions", status=status)


@mcp.tool()
async def find_by_prize(min_prize: int = 10000, opportunity_type: str = "competitions", status: str = "open", per_page: int = 20) -> dict:
    """Find competitions or hackathons with a minimum cash prize pool, sorted highest first.

    Args:
        min_prize: Minimum total cash prize in INR (e.g. 50000 for ₹50k+).
        opportunity_type: competitions | hackathons.
        per_page: How many to scan (max 50; higher = better recall).
    """
    opportunity_type = opportunity_type.lower().strip()
    if opportunity_type not in ("competitions", "hackathons"):
        return {"error": "opportunity_type must be 'competitions' or 'hackathons'."}
    err = _validate(opportunity_type, status)
    if err:
        return {"error": err}

    try:
        data = await _fetch({"opportunity": opportunity_type, "oppstatus": status, "page": 1, "per_page": min(per_page, 50)})
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    matched = sorted([(it, _total_cash(it.get("prizes"))) for it in items if _total_cash(it.get("prizes")) >= min_prize], key=lambda x: x[1], reverse=True)
    results = [{**_summarize(it), "total_prize_cash": cash} for it, cash in matched]

    return {
        "type": opportunity_type, "status": status, "min_prize": f"₹{min_prize:,}",
        "scanned": len(items), "matched": len(results), "results": results,
        "note": "Increase per_page (max 50) for broader coverage." if data.get("total", 0) > per_page else None,
    }


@mcp.tool()
async def find_closing_soon(days: int = 7, opportunity_type: str = "competitions", per_page: int = 30) -> dict:
    """Find open opportunities whose registration closes within the next N days, sorted soonest first.

    Args:
        days: Window in days (e.g. 3 = closing in the next 3 days).
        opportunity_type: competitions | hackathons | jobs | internships | scholarships.
        per_page: How many open listings to scan (max 50).
    """
    opportunity_type = opportunity_type.lower().strip()
    err = _validate(opportunity_type, "open")
    if err:
        return {"error": err}
    if days < 0:
        return {"error": "days must be >= 0."}

    try:
        data = await _fetch({"opportunity": opportunity_type, "oppstatus": "open", "page": 1, "per_page": min(per_page, 50)})
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}

    items = data.get("data") or []
    matched = sorted([(it, d) for it in items for d in [_days_left(it)] if d is not None and d <= days], key=lambda x: x[1])
    results = [{**_summarize(it), "days_left": d} for it, d in matched]

    return {
        "type": opportunity_type, "closing_within_days": days,
        "scanned": len(items), "matched": len(results), "results": results,
        "note": "Increase per_page or check more pages for completeness." if data.get("total", 0) > per_page else None,
    }


@mcp.tool()
async def list_open_competitions(limit: int = 10) -> dict:
    """List competitions currently open for registration, newest first."""
    limit = max(1, min(limit, 50))
    try:
        data = await _fetch({"opportunity": "competitions", "oppstatus": "open", "page": 1, "per_page": limit})
    except httpx.HTTPError as e:
        return {"error": f"Unstop API error: {e}"}
    items = data.get("data") or []
    return {"total_open": data.get("total"), "count": len(items), "competitions": [_summarize(it) for it in items]}


# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unstop MCP server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                        help="stdio (default) for Claude Desktop/Code; sse for remote HTTP connector")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "sse":
        # FastMCP auto-enables DNS rebinding protection when the initial host is
        # 127.0.0.1/localhost, locking allowed_hosts to localhost only. Behind a
        # reverse proxy (Render, Railway, etc.) the Host header is the external
        # domain, causing 421 errors. Disable it here using the official API.
        from mcp.server.transport_security import TransportSecuritySettings
        mcp.settings.transport_security = TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
