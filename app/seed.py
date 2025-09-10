from typing import Dict, List

from sqlalchemy.orm import Session

from app.models import Sport, Round


SPORTS: List[Dict[str, str]] = [
    {"sports_code": "sx", "name": "Supercross"},
    {"sports_code": "mx", "name": "Motocross"},
    {"sports_code": "smx", "name": "SuperMotocross"},
]


ROUND_CODES: List[Dict[str, str]] = [
    {"code": "PRACTICE", "name": "Practice"},
    {"code": "QUALIFYING", "name": "Qualifying"},
    {"code": "HEAT", "name": "Heat"},
    {"code": "LCQ", "name": "Last Chance Qualifier"},
    {"code": "MAIN_EVENT", "name": "Main Event"},
    {"code": "RACE", "name": "Race"},
    {"code": "FINAL", "name": "Final"},
]


def get_or_create_sport(session: Session, sports_code: str, name: str) -> Sport:
    sport = session.query(Sport).filter_by(sports_code=sports_code).one_or_none()
    if sport:
        return sport
    sport = Sport(sports_code=sports_code, name=name)
    session.add(sport)
    session.flush()
    return sport


def get_or_create_round(session: Session, code: str, name: str, sports_id) -> Round:
    # code is UNIQUE in schema; filter by code only
    rnd = session.query(Round).filter_by(code=code).one_or_none()
    if rnd:
        return rnd
    rnd = Round(sports_id=sports_id, code=code, name=name)
    session.add(rnd)
    session.flush()
    return rnd


def seed_all(session: Session) -> None:
    # Ensure sports exist
    created_sports = {}
    for s in SPORTS:
        sport = get_or_create_sport(session, s["sports_code"], s["name"])
        created_sports[s["sports_code"]] = sport

    # Rounds table requires sports_id and code is unique globally.
    # Seed once under SMX as the canonical set.
    smx_sport = created_sports.get("smx")
    for r in ROUND_CODES:
        get_or_create_round(session, r["code"], r["name"], smx_sport.id)

    session.commit()


