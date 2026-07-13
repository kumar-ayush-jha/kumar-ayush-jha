#!/usr/bin/env python3
"""
fetch_contributions.py — scrapes the public contribution calendar for a user
with no auth / no token, using the same endpoint your profile page's graph
loads from. Writes data/contributions.json.

Usage:
    GH_PROFILE_USER=your-username python scripts/fetch_contributions.py
"""
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "").strip()
OUT = Path("data/contributions.json")


def fetch_calendar(username: str) -> dict:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day"):
        date = cell.get("data-date")
        count = cell.get("data-count")
        if date is None:
            continue
        days.append({"date": date, "count": int(count) if count else 0})

    if not days:
        raise RuntimeError(
            "no contribution cells found — GitHub may have changed markup; "
            "check the ContributionCalendar-day selector"
        )

    days.sort(key=lambda d: d["date"])

    total = sum(d["count"] for d in days)
    streak = 0
    best_streak = 0
    for d in days:
        if d["count"] > 0:
            streak += 1
            best_streak = max(best_streak, streak)
        else:
            streak = 0

    return {
        "username": username,
        "days": days,
        "total": total,
        "best_streak": best_streak,
    }


def main():
    if not USERNAME:
        raise SystemExit("set GH_PROFILE_USER to your GitHub username")
    data = fetch_calendar(USERNAME)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2))
    print(f"wrote {OUT}  ({len(data['days'])} days, {data['total']} total, best streak {data['best_streak']})")


if __name__ == "__main__":
    main()
