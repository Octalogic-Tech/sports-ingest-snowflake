import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import SessionLocal
from models import (
    Sports, Tours, TourYears, Events, Teams,
    Players, EventParticipants, Rounds,
    EventRounds, Scores
)

SCHEDULE_URL = "https://results.supermotocross.com/events/"
API_KEY = "9981aae9-7668-46a1-a0d6-b03efa26bb90"

def fetch_events():
    """Scrape schedule page to get event IDs and names."""
    response = requests.get(SCHEDULE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    for link in soup.select("a[href*='view_event']"):
        event_name = link.text.strip()
        href = link["href"]
        if "id=" in href:
            event_id = href.split("id=")[-1]
            events.append({"api_id": event_id, "name": event_name})

    return events

def fetch_event_details(api_id: str):
    """Fetch detailed event info from API."""
    url = f"https://results.supermotocross.com/results?p=view_event&export=json&key={API_KEY}&id={api_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch event {api_id}")
        return None

    data = response.json().get("event", {})
    if not data:
        print(f"⚠️ No details found for event {api_id}")
        return None

    # Determine sport type
    domain = data.get("domain_config")
    if domain == "sx":
        sport_code = "supercross"
    elif domain == "mx":
        sport_code = "motocross"
    elif domain == "smx":
        sport_code = "supermotocross"
    else:
        sport_code = "unknown"

    return {
        "api_id": api_id,
        "name": data.get("event_name"),
        "venue": data.get("track_name"),
        "start_date": data.get("start_date_time"),
        "sport_code": sport_code,
        "teams": data.get("teams", []),
        "rounds": data.get("rounds", [])
    }

def get_or_create_sport(session, sport_code: str):
    sport = session.query(Sports).filter_by(sports_code=sport_code).first()
    if not sport:
        sport = Sports(sports_code=sport_code, name=sport_code.capitalize())
        session.add(sport)
        session.commit()
    return sport

def get_or_create_tour(session, sport_id: uuid.UUID):
    tour = session.query(Tours).filter_by(sports_id=sport_id).first()
    if not tour:
        tour = Tours(sports_id=sport_id, name="Default Tour")
        session.add(tour)
        session.commit()
    return tour

def get_or_create_tour_year(session, sport_id: uuid.UUID, tour_id: uuid.UUID):
    tour_year = session.query(TourYears).filter_by(sports_id=sport_id, tour_id=tour_id).first()
    if not tour_year:
        tour_year = TourYears(sports_id=sport_id, tour_id=tour_id, name="2025 Season")
        session.add(tour_year)
        session.commit()
    return tour_year

def get_or_create_team(session, sport_id: uuid.UUID, team_name: str):
    team = session.query(Teams).filter_by(name=team_name, sports_id=sport_id).first()
    if not team:
        team = Teams(name=team_name, sports_id=sport_id)
        session.add(team)
        session.commit()
    return team

def get_or_create_player(session, sport_id: uuid.UUID, player_name: str, team_id: uuid.UUID = None):
    player = session.query(Players).filter_by(name=player_name, sports_id=sport_id).first()
    if not player:
        player = Players(name=player_name, sports_id=sport_id, team_id=team_id)
        session.add(player)
        session.commit()
    return player

def create_event(session, details: dict, sport: Sports, tour_year: TourYears):
    existing = session.query(Events).filter_by(api_id=details["api_id"]).first()
    if existing:
        return existing

    event = Events(
        api_id=details["api_id"],
        name=details["name"],
        venue=details["venue"],
        start_date=details["start_date"],
        sports_id=sport.id,
        tour_year_id=tour_year.id
    )
    session.add(event)
    session.commit()
    return event

def create_event_participants(session, event: Events, sport: Sports, teams: list):
    """Create teams and players for an event."""
    for team_info in teams:
        team_name = team_info.get("name")
        team = get_or_create_team(session, sport.id, team_name)
        for player_name in team_info.get("drivers", []):
            player = get_or_create_player(session, sport.id, player_name, team.id)
            # Link player as participant
            participant = EventParticipants(
                sports_id=sport.id,
                event_id=event.id,
                team_id=team.id,
                player_id=player.id,
                role="driver"
            )
            session.add(participant)
    session.commit()

def create_rounds_and_scores(session, event: Events, sport: Sports, rounds: list):
    """Create rounds and scores for each event."""
    for r in rounds:
        round_obj = Rounds(
            sports_id=sport.id,
            code=r.get("code"),
            name=r.get("name"),
            round_no=r.get("round_no")
        )
        session.add(round_obj)
        session.commit()

        event_round = EventRounds(
            sports_id=sport.id,
            event_id=event.id,
            round_id=round_obj.id,
            order_in_parent=r.get("round_no")
        )
        session.add(event_round)
        session.commit()

        # Add scores
        results_api = f"https://results.supermotocross.com/results?p=view_race_result&export=json&key={API_KEY}&id={r.get('race_id')}"
        res_resp = requests.get(results_api)
        if res_resp.status_code != 200:
            continue
        results = res_resp.json().get("results", [])
        for result in results:
            player_name = result.get("driver_name")
            score_value = result.get("score")
            player = get_or_create_player(session, sport.id, player_name)
            participant = session.query(EventParticipants).filter_by(player_id=player.id, event_id=event.id).first()
            if not participant:
                participant = EventParticipants(
                    sports_id=sport.id,
                    event_id=event.id,
                    player_id=player.id,
                    role="driver"
                )
                session.add(participant)
                session.commit()
            score = Scores(
                sports_id=sport.id,
                event_id=event.id,
                event_round_id=event_round.id,
                event_participant_id=participant.id,
                metric_key="score",
                metric_value=score_value
            )
            session.add(score)
    session.commit()

def save_events_to_db():
    session = SessionLocal()
    events_list = fetch_events()
    for e in events_list:
        details = fetch_event_details(e["api_id"])
        if not details:
            continue

        sport = get_or_create_sport(session, details["sport_code"])
        tour = get_or_create_tour(session, sport.id)
        tour_year = get_or_create_tour_year(session, sport.id, tour.id)
        event = create_event(session, details, sport, tour_year)
        create_event_participants(session, event, sport, details.get("teams", []))
        create_rounds_and_scores(session, event, sport, details.get("rounds", []))

    session.close()
    print("✅ All events, participants, rounds, and scores inserted successfully.")

if __name__ == "__main__":
    print("Fetching events and saving to DB...")
    save_events_to_db()
