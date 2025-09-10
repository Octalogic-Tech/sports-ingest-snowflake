from typing import Dict, List, Optional

import re
import urllib.parse

import requests
from bs4 import BeautifulSoup


EVENTS_URL = "https://results.supermotocross.com/events/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _extract_id_from_url(url: str) -> Optional[int]:
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "tournament" in qs and qs["tournament"]:
            return int(qs["tournament"][0])
        if "id" in qs and qs["id"]:
            return int(qs["id"][0])
    except Exception:
        pass

    match = re.search(r"(?:id|tournament)=([0-9]{4,})", url)
    if match:
        try:
            return int(match.group(1))
        except Exception:
            return None
    return None


def scrape_events() -> List[Dict]:
    resp = requests.get(
        EVENTS_URL,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
        timeout=30,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    events: List[Dict] = []

    # Broaden selectors in case markup differs
    anchors = soup.select("a[href*='/events']")
    seen = set()
    for a in anchors:
        href = a.get("href", "").strip()
        if not href:
            continue
        full_url = urllib.parse.urljoin(EVENTS_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        tournament_id = _extract_id_from_url(full_url)
        title = a.get_text(strip=True) or full_url
        events.append({
            "title": title,
            "url": full_url,
            "tournament_id": tournament_id,
        })

    # Keep only those where we found an ID, but return all if none found
    with_ids = [e for e in events if e["tournament_id"] is not None]
    return with_ids if with_ids else events


