from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://results.supermotocross.com/results"
API_KEY = "9981aae9-7668-46a1-a0d6-b03efa26bb90"


class SmxApiClient:
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()
        # Configure retries for transient failures and rate limits
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.get(
            BASE_URL,
            params={"export": "json", "key": API_KEY, **params},
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()

    def get_event_details(self, event_id: int) -> Dict[str, Any]:
        return self._get({"p": "view_event", "id": event_id})

    def get_race_results(self, race_id: int) -> Dict[str, Any]:
        return self._get({"p": "view_race_result", "id": race_id})


