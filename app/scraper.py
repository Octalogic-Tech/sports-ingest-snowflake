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
    # Collect anchors that are likely to point to specific events rather than the listing itself
    anchors = []
    selector_candidates = [
        "a[href*='view_event']",
        "a[href*='p=view_event']",
        "a[href*='?id=']",
        "a[href*='&id=']",
        "a[href*='tournament=']",
        "a[href*='/events/']",
    ]
    for sel in selector_candidates:
        anchors.extend(soup.select(sel))
    seen = set()
    for a in anchors:
        href = a.get("href", "").strip()
        if not href:
            continue
        full_url = urllib.parse.urljoin(EVENTS_URL, href)
        # Skip the listing page itself
        if full_url.rstrip("/") == EVENTS_URL.rstrip("/"):
            continue
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
    if with_ids:
        return with_ids

    # Fallback: scan all anchors' hrefs with regex when selectors miss
    fallback_events: List[Dict] = []
    seen_fallback = set()
    for a in soup.find_all("a"):
        href = a.get("href", "").strip()
        if not href:
            continue
        full_url = urllib.parse.urljoin(EVENTS_URL, href)
        if full_url in seen_fallback:
            continue
        seen_fallback.add(full_url)
        tid = _extract_id_from_url(full_url)
        if tid is None:
            continue
        title = a.get_text(strip=True) or full_url
        fallback_events.append({
            "title": title,
            "url": full_url,
            "tournament_id": tid,
        })

    return fallback_events if fallback_events else events


