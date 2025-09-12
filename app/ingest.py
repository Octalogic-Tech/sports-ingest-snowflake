from typing import Any, Dict, Optional, Iterable, List, Tuple

from sqlalchemy.orm import Session

from app.models import Sport, Event, Tour, TourYear, Round, EventRound, Team, Player, EventParticipant, Score
from app.smx_api import SmxApiClient


def _map_domain_to_code(domain_config: Optional[str]) -> Optional[str]:
    if not domain_config:
        return None
    domain = (domain_config or "").strip().lower()
    if domain in {"sx", "supercross"}:
        return "sx"
    if domain in {"mx", "motocross"}:
        return "mx"
    if domain in {"smx", "supermotocross", "super moto cross"}:
        return "smx"
    return None


def _get_or_create_sport_by_code(session: Session, sports_code: str, name_fallback: str) -> Sport:
    sport = session.query(Sport).filter_by(sports_code=sports_code).one_or_none()
    if sport:
        return sport
    sport = Sport(sports_code=sports_code, name=name_fallback)
    session.add(sport)
    session.flush()
    return sport


def _get_or_create_tour(session: Session, sports_id, name: str) -> Tour:
    tour = (
        session.query(Tour)
        .filter(Tour.sports_id == sports_id)
        .filter(Tour.name == name)
        .one_or_none()
    )
    if tour:
        return tour
    tour = Tour(sports_id=sports_id, name=name)
    session.add(tour)
    session.flush()
    return tour


def _get_or_create_tour_year(session: Session, sports_id, tour_id, name: str) -> TourYear:
    ty = (
        session.query(TourYear)
        .filter(TourYear.sports_id == sports_id)
        .filter(TourYear.tour_id == tour_id)
        .filter(TourYear.name == name)
        .one_or_none()
    )
    if ty:
        return ty
    ty = TourYear(sports_id=sports_id, tour_id=tour_id, name=name)
    session.add(ty)
    session.flush()
    return ty


def _parse_event_year(event_payload: Dict[str, Any]) -> str:
    # Try event.start_date_time like "2025-08-16 00:00"
    evt = event_payload.get("event") or {}
    sdt: Optional[str] = evt.get("start_date_time") or evt.get("start_date_time_display")
    if isinstance(sdt, str) and len(sdt) >= 4 and sdt[:4].isdigit():
        return sdt[:4]
    # Try any session start date
    sessions = event_payload.get("sessions") or []
    for sess in sessions:
        s = sess.get("start_date_time")
        if isinstance(s, str) and len(s) >= 4 and s[:4].isdigit():
            return s[:4]
    # Fallback
    return "Unknown"


def _upsert_event(
    session: Session,
    sports_id,
    tour_year_id,
    name: str,
    meta: Dict[str, Any],
) -> Event:
    # Use name + sports_id as a simple idempotency key
    ev = (
        session.query(Event)
        .filter(Event.sports_id == sports_id)
        .filter(Event.name == name)
        .one_or_none()
    )
    if ev:
        ev.meta = meta
        session.flush()
        return ev
    # Extract some optional fields
    evt = meta.get("event") or {}
    start_date = None
    end_date = None
    venue = evt.get("track_name") or evt.get("venue")
    ev = Event(
        sports_id=sports_id,
        tour_year_id=tour_year_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        venue=venue,
        meta=meta,
    )
    session.add(ev)
    session.flush()
    return ev


def ingest_event(session: Session, event_id: int) -> Dict[str, Any]:
    client = SmxApiClient()
    data = client.get_event_details(event_id)

    domain_config = data.get("domain_config")
    sport_code = _map_domain_to_code(domain_config) or "smx"

    sport_name = {"sx": "Supercross", "mx": "Motocross", "smx": "SuperMotocross"}.get(sport_code, "SuperMotocross")
    sport = _get_or_create_sport_by_code(session, sport_code, sport_name)

    name = data.get("event_name") or data.get("name") or f"Event {event_id}"
    # Create/find tour + year
    tour = _get_or_create_tour(session, sport.id, f"{sport_name} Tour")
    year_name = _parse_event_year(data)
    tour_year = _get_or_create_tour_year(session, sport.id, tour.id, year_name)

    ev = _upsert_event(session, sport.id, tour_year.id, name, data)
    session.commit()

    return {"event_id": str(ev.id), "sports_code": sport_code, "name": name}


def _find_first_list_of_dicts(node: Any) -> Optional[List[Dict[str, Any]]]:
    if isinstance(node, list):
        if node and isinstance(node[0], dict):
            return node  # type: ignore[return-value]
        for item in node:
            found = _find_first_list_of_dicts(item)
            if found is not None:
                return found
    elif isinstance(node, dict):
        for v in node.values():
            found = _find_first_list_of_dicts(v)
            if found is not None:
                return found
    return None


def _extract_race_ids(event_payload: Dict[str, Any]) -> List[int]:
    race_ids: List[int] = []
    # Look for common keys
    def scan(node: Any):
        if isinstance(node, dict):
            for k, v in node.items():
                kl = str(k).lower()
                if kl in {"race_id", "result_id"}:
                    try:
                        vi = int(v)
                        race_ids.append(vi)
                    except Exception:
                        pass
                scan(v)
        elif isinstance(node, list):
            for item in node:
                scan(item)

    scan(event_payload)
    # De-duplicate
    return sorted({rid for rid in race_ids})


def _get_or_create_round(session: Session, sports_id, code: str, name: str) -> Round:
    rnd = session.query(Round).filter_by(code=code).one_or_none()
    if rnd:
        return rnd
    rnd = Round(sports_id=sports_id, code=code, name=name)
    session.add(rnd)
    session.flush()
    return rnd


def _get_or_create_event_round(session: Session, sports_id, event_id, round_id) -> EventRound:
    er = (
        session.query(EventRound)
        .filter(EventRound.sports_id == sports_id)
        .filter(EventRound.event_id == event_id)
        .filter(EventRound.round_id == round_id)
        .one_or_none()
    )
    if er:
        return er
    er = EventRound(sports_id=sports_id, event_id=event_id, round_id=round_id)
    session.add(er)
    session.flush()
    return er


def _get_or_create_team(session: Session, sports_id, name: Optional[str]) -> Optional[Team]:
    if not name:
        return None
    team = (
        session.query(Team)
        .filter(Team.sports_id == sports_id)
        .filter(Team.name == name)
        .one_or_none()
    )
    if team:
        return team
    team = Team(sports_id=sports_id, name=name)
    session.add(team)
    session.flush()
    return team


def _get_or_create_player(session: Session, sports_id, name: str, team_id: Optional[str]) -> Player:
    player = (
        session.query(Player)
        .filter(Player.sports_id == sports_id)
        .filter(Player.name == name)
        .one_or_none()
    )
    if player:
        # update team if missing
        if team_id and player.team_id is None:
            player.team_id = team_id
            session.flush()
        return player
    player = Player(sports_id=sports_id, name=name, team_id=team_id)
    session.add(player)
    session.flush()
    return player


def _get_or_create_event_participant(session: Session, sports_id, event_id, player_id, team_id) -> EventParticipant:
    ep = (
        session.query(EventParticipant)
        .filter(EventParticipant.sports_id == sports_id)
        .filter(EventParticipant.event_id == event_id)
        .filter(EventParticipant.player_id == player_id)
        .one_or_none()
    )
    if ep:
        # Backfill team if available
        if team_id and ep.team_id is None:
            ep.team_id = team_id
            session.flush()
        return ep
    ep = EventParticipant(sports_id=sports_id, event_id=event_id, player_id=player_id, team_id=team_id, role="driver")
    session.add(ep)
    session.flush()
    return ep


def _insert_score(session: Session, sports_id, event_id, event_round_id, event_participant_id, metric_key: str, metric_value: Dict[str, Any]) -> None:
    sc = Score(
        sports_id=sports_id,
        event_id=event_id,
        event_round_id=event_round_id,
        event_participant_id=event_participant_id,
        metric_key=metric_key,
        metric_value=metric_value,
    )
    session.add(sc)


def ingest_event_full(session: Session, event_id: int) -> Dict[str, Any]:
    client = SmxApiClient()
    data = client.get_event_details(event_id)

    domain_config = data.get("domain_config")
    sport_code = _map_domain_to_code(domain_config) or "smx"
    sport_name = {"sx": "Supercross", "mx": "Motocross", "smx": "SuperMotocross"}.get(sport_code, "SuperMotocross")
    sport = _get_or_create_sport_by_code(session, sport_code, sport_name)

    name = data.get("event_name") or data.get("name") or f"Event {event_id}"
    tour = _get_or_create_tour(session, sport.id, f"{sport_name} Tour")
    year_name = _parse_event_year(data)
    tour_year = _get_or_create_tour_year(session, sport.id, tour.id, year_name)

    ev = _upsert_event(session, sport.id, tour_year.id, name, data)

    # Ensure a generic RACE round exists and link event_round
    race_round = _get_or_create_round(session, sport.id, "RACE", "Race")
    event_round = _get_or_create_event_round(session, sport.id, ev.id, race_round.id)

    # Pull race ids from event details, then fetch and persist results
    race_ids = _extract_race_ids(data)
    fetched = 0
    for rid in race_ids:
        try:
            rr = client.get_race_results(rid)
        except Exception:
            continue
        fetched += 1
        # First, prefer explicit drivers object with laps
        inserted_rows = 0
        drivers = None
        race_obj = rr.get("race") if isinstance(rr, dict) else None
        if isinstance(race_obj, dict):
            drivers = race_obj.get("drivers")
        winner_candidate = None  # (ep_id, player_name, team_name, final_pos)
        if isinstance(drivers, dict):
            for _driver_id, d in drivers.items():
                if not isinstance(d, dict):
                    continue
                # Extract identity
                name = (
                    d.get("name")
                    or d.get("rider")
                    or d.get("driver")
                    or d.get("display_name")
                    or d.get("Rider")
                    or d.get("Driver")
                )
                team_name = (
                    d.get("team")
                    or d.get("Team")
                    or d.get("manufacturer")
                    or d.get("Manufacturer")
                    or d.get("bike")
                    or d.get("Bike")
                )
                if not name:
                    # Try combining first/last
                    first = d.get("FirstName") or d.get("first_name")
                    last = d.get("LastName") or d.get("last_name")
                    if first or last:
                        name = f"{first or ''} {last or ''}".strip()
                if not name:
                    continue

                team = _get_or_create_team(session, sport.id, str(team_name) if team_name else None)
                player = _get_or_create_player(session, sport.id, str(name), team.id if team else None)
                ep = _get_or_create_event_participant(session, sport.id, ev.id, player.id, team.id if team else None)

                # Store driver summary
                _insert_score(
                    session,
                    sport.id,
                    ev.id,
                    event_round.id,
                    ep.id,
                    "race_driver",
                    d,
                )
                inserted_rows += 1

                # Store each lap as a separate metric row
                laps = d.get("laps")
                if isinstance(laps, list):
                    # Track final position from last lap with valid 'pos'
                    last_pos_val = None
                    for lap in laps:
                        if not isinstance(lap, dict):
                            continue
                        _insert_score(
                            session,
                            sport.id,
                            ev.id,
                            event_round.id,
                            ep.id,
                            "race_lap",
                            lap,
                        )
                        lp = lap.get("pos") or lap.get("position")
                        try:
                            last_pos_val = int(str(lp)) if lp is not None else last_pos_val
                        except Exception:
                            pass
                    if last_pos_val is not None:
                        # Record final position for winner determination later
                        if last_pos_val == 1:
                            winner_candidate = (ep.id, player.name, team.name if team else None, last_pos_val)

        # Heuristic: find list of results
        results_list: Optional[List[Dict[str, Any]]] = None
        for key in ["results", "racers", "rows", "data", "positions", "Results", "Rows"]:
            val = rr.get(key)
            if isinstance(val, list) and val and isinstance(val[0], dict):
                results_list = val  # type: ignore[assignment]
                break
        if results_list is None:
            results_list = _find_first_list_of_dicts(rr)

        for row in (results_list or []):
            name_fields = [
                "rider", "driver", "name", "racer", "athlete",
                "Rider", "Driver", "Name",
                "RiderName", "rider_name",
            ]
            team_fields = [
                "team", "Team", "team_name", "TeamName",
                "constructor", "manufacturer", "Manufacturer", "bike", "Bike",
            ]
            player_name = None
            team_name = None
            for nf in name_fields:
                if row.get(nf):
                    player_name = str(row[nf])
                    break
            if not player_name:
                # Try combine first/last
                first = row.get("FirstName") or row.get("first_name")
                last = row.get("LastName") or row.get("last_name")
                if first or last:
                    player_name = f"{first or ''} {last or ''}".strip()
            for tf in team_fields:
                if row.get(tf):
                    team_name = str(row[tf])
                    break
            if not player_name:
                continue

            team = _get_or_create_team(session, sport.id, team_name)
            player = _get_or_create_player(session, sport.id, player_name, team.id if team else None)
            ep = _get_or_create_event_participant(session, sport.id, ev.id, player.id, team.id if team else None)

            # store the entire row as score metric for traceability; key by source 'race_result'
            _insert_score(
                session,
                sport.id,
                ev.id,
                event_round.id,
                ep.id,
                "race_result",
                row,
            )
            inserted_rows += 1

        # If we couldn't parse any rows, store the raw payload on the event_round metadata
        if inserted_rows == 0:
            try:
                # merge existing meta if present
                existing = event_round.meta or {}
                if isinstance(existing, dict):
                    existing.setdefault("race_payloads", []).append(rr)
                    event_round.meta = existing
                else:
                    event_round.meta = {"race_payloads": [rr]}
                session.flush()
            except Exception:
                # swallow metadata save errors to avoid failing the whole ingest
                pass

        # If we identified a winner from laps, upsert a winner score
        if winner_candidate is not None:
            ep_id, player_name, team_name, final_pos = winner_candidate
            _insert_score(
                session,
                sport.id,
                ev.id,
                event_round.id,
                ep_id,
                "winner",
                {
                    "player_name": player_name,
                    "team_name": team_name,
                    "final_pos": final_pos,
                    "race_id": rid,
                },
            )

    session.commit()
    return {"event_id": str(ev.id), "sports_code": sport_code, "name": name, "races_processed": fetched}


