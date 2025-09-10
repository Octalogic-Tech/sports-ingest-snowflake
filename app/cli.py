import argparse
import json

from app.db import SessionLocal
from app.seed import seed_all
from app.ingest import ingest_event, ingest_event_full
from app.scraper import scrape_events
from app.smx_api import SmxApiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Sports MVP utilities")
    parser.add_argument("command", choices=["seed", "scrape", "event", "race", "ingest_event", "ingest_event_full", "ingest_many"], help="Action to perform")
    parser.add_argument("id", nargs="?", help="Event or race id for API fetch")
    args = parser.parse_args()

    if args.command == "seed":
        with SessionLocal() as session:
            seed_all(session)
        print("Seed completed")
        return

    if args.command == "scrape":
        events = scrape_events()
        print(json.dumps(events[:25], indent=2))
        return

    client = SmxApiClient()
    if args.command == "event":
        if not args.id:
            raise SystemExit("Provide event id")
        data = client.get_event_details(int(args.id))
        print(json.dumps(data, indent=2))
        return

    if args.command == "race":
        if not args.id:
            raise SystemExit("Provide race id")
        data = client.get_race_results(int(args.id))
        print(json.dumps(data, indent=2))
        return

    if args.command == "ingest_event":
        if not args.id:
            raise SystemExit("Provide event id")
        with SessionLocal() as session:
            out = ingest_event(session, int(args.id))
        print(json.dumps(out, indent=2))
        return

    if args.command == "ingest_event_full":
        if not args.id:
            raise SystemExit("Provide event id")
        with SessionLocal() as session:
            out = ingest_event_full(session, int(args.id))
        print(json.dumps(out, indent=2))
        return

    if args.command == "ingest_many":
        if not args.id:
            raise SystemExit("Provide ids: e.g. 477866,477867 or 477860-477870")
        ids = []
        if "," in args.id:
            ids = [int(x) for x in args.id.split(",") if x.strip().isdigit()]
        elif "-" in args.id:
            a, b = args.id.split("-", 1)
            ids = list(range(int(a), int(b) + 1))
        else:
            ids = [int(args.id)]

        results = []
        with SessionLocal() as session:
            for eid in ids:
                try:
                    results.append(ingest_event_full(session, int(eid)))
                except Exception as e:
                    results.append({"event_id": eid, "error": str(e)})
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()


