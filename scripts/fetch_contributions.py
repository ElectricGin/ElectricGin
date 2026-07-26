#!/usr/bin/env python3
"""Fetch a GitHub user's public contribution calendar (no token needed) and
write derived stats to data/contributions.json."""
import datetime
import json
import os
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "ElectricGin")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.find_all("td", attrs={"data-date": True})
    if not cells:
        cells = soup.find_all("rect", attrs={"data-date": True})

    for cell in cells:
        date = cell["data-date"]
        level = cell.get("data-level")
        if level is not None:
            level = int(level)
        else:
            title = cell.get("title", "") or cell.get("aria-label", "")
            count = 0
            for token in title.replace(",", "").split():
                if token.isdigit():
                    count = int(token)
                    break
            level = min(4, (count > 0) + (count >= 3) + (count >= 6) + (count >= 10))
        days.append({"date": date, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    total = 0
    counts_by_month = {}
    current_streak = 0
    longest_streak = 0
    running = 0
    best_day = None
    best_level = -1

    today = datetime.date.today()
    for day in days:
        level = day["level"]
        if level > best_level:
            best_level = level
            best_day = day["date"]
        month = day["date"][:7]
        counts_by_month[month] = counts_by_month.get(month, 0) + (1 if level > 0 else 0)
        if level > 0:
            total += 1
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    for day in reversed(days):
        if day["date"] > today.isoformat():
            continue
        if day["level"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total_active_days": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "counts_by_month": counts_by_month,
    }


def main():
    days = fetch_days()
    if not days:
        print("no contribution data parsed; aborting without overwriting existing file", file=sys.stderr)
        sys.exit(1)

    stats = derive_stats(days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"wrote {len(days)} days to {OUT_PATH}")


if __name__ == "__main__":
    main()
