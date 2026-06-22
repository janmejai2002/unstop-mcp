"""Smoke test — calls every tool against the live Unstop API."""
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
import server

SEP = "\n" + "─" * 60

async def main():
    print("=== get_platform_stats ===")
    s = await server.get_platform_stats()
    print(f"  total_open: {s['total_open']}")
    for t, v in s["by_type"].items():
        print(f"  {t}: open={v.get('open')}  closed={v.get('closed')}")

    print(SEP)
    print("=== list_open_competitions(limit=3) ===")
    r = await server.list_open_competitions(limit=3)
    for c in r["competitions"]:
        print(f"  [{c['id']}] {c['title']} | {c['prize']} | {c['time_left']}")

    print(SEP)
    print("=== search_hackathons(query='AI', per_page=3) ===")
    r = await server.search_hackathons(query="AI", per_page=3)
    print(f"  total={r['total']}")
    for c in r["results"]:
        print(f"  [{c['id']}] {c['title']} ({c['location']})")

    print(SEP)
    print("=== search_jobs(work_type='remote', per_page=5) ===")
    r = await server.search_jobs(work_type="remote", per_page=5)
    for c in r["results"]:
        print(f"  [{c['id']}] {c['title']} | {c.get('salary','?')} | {c.get('work_type','?')}")

    print(SEP)
    print("=== search_internships(min_stipend=15000, per_page=5) ===")
    r = await server.search_internships(min_stipend=15000, per_page=5)
    print(f"  count={r['count']}")
    for c in r["results"]:
        print(f"  [{c['id']}] {c['title']} | {c.get('salary','?')}")

    print(SEP)
    print("=== find_by_prize(min_prize=50000, hackathons) ===")
    r = await server.find_by_prize(min_prize=50000, opportunity_type="hackathons", per_page=30)
    print(f"  scanned={r['scanned']}  matched={r['matched']}")
    for c in r["results"]:
        print(f"  [{c['id']}] {c['title']} | cash=₹{c.get('total_prize_cash',0):,}")

    print(SEP)
    print("=== find_closing_soon(days=5, competitions) ===")
    r = await server.find_closing_soon(days=5, opportunity_type="competitions", per_page=40)
    print(f"  matched={r['matched']}")
    for c in r["results"]:
        print(f"  [{c['id']}] {c['title']} | {c.get('days_left')}d left")

    print(SEP)
    print("ALL TESTS PASSED")

asyncio.run(main())
