from typing import Any, Dict, Optional

import requests


BASE_URL = "https://results.supermotocross.com/results"
API_KEY = "9981aae9-7668-46a1-a0d6-b03efa26bb90"


class SmxApiClient:
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()

    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.get(BASE_URL, params={"export": "json", "key": API_KEY, **params}, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_event_details(self, event_id: int) -> Dict[str, Any]:
        return self._get({"p": "view_event", "id": event_id})

    def get_race_results(self, race_id: int) -> Dict[str, Any]:
        return self._get({"p": "view_race_result", "id": race_id})


