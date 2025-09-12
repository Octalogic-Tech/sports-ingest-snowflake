import argparse
import json

from app.db import SessionLocal
from app.seed import seed_all
from app.ingest import ingest_event, ingest_event_full, ingest_all_visible_events
from app.scraper import scrape_events
from app.smx_api import SmxApiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Sports MVP utilities")
    parser.add_argument("command", choices=["seed", "scrape", "event", "race", "ingest_event", "ingest_event_full", "ingest_many", "ingest_all"], help="Action to perform")
    parser.add_argument("id", nargs="?", help="Event or race id for API fetch")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of events to ingest for ingest_all")
    args = parser.parse_args()

    if args.command == "seed":
        with SessionLocal() as session:
            seed_all(session)
        print("Seed completed")
        return

    if args.command == "scrape":
        events = scrape_events()
        total = len(events)
        unique_ids = len({e.get("tournament_id") for e in events if e.get("tournament_id") is not None})
        print(json.dumps({"discovered_events": total, "unique_ids": unique_ids}, indent=2))
        print(json.dumps(events, indent=2))
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
        return

    if args.command == "ingest_all":
        # Stream progress so it doesn't appear stuck for long runs
        events = scrape_events()
        if args.limit is not None and args.limit >= 0:
            events = events[: args.limit]
        total = len(events)
        print(json.dumps({"message": "Discovered events", "count": total}, indent=2))

        results = []
        processed = 0
        try:
            with SessionLocal() as session:
                for e in events:
                    eid = e.get("tournament_id") or e.get("id") or e.get("event_id")
                    title = e.get("title") or ""
                    url = e.get("url") or ""
                    if eid is None:
                        res = {"url": url, "title": title, "error": "missing_event_id"}
                        results.append(res)
                        processed += 1
                        print(json.dumps({"progress": f"{processed}/{total}", "skipped": res}, indent=2))
                        continue
                    try:
                        out = ingest_event_full(session, int(eid))
                        out.update({"source_url": url, "source_title": title})
                        results.append(out)
                        processed += 1
                        print(json.dumps({"progress": f"{processed}/{total}", "ok": {"event_id": out.get("event_id"), "name": out.get("name"), "races_processed": out.get("races_processed")}}, indent=2))
                    except Exception as ex:
                        err = {"event_id": eid, "url": url, "title": title, "error": str(ex)}
                        results.append(err)
                        processed += 1
                        print(json.dumps({"progress": f"{processed}/{total}", "error": err}, indent=2))
        except KeyboardInterrupt:
            print(json.dumps({"message": "Interrupted by user", "processed": processed, "total": total}, indent=2))

        print(json.dumps({"summary": {"processed": processed, "total": total}}, indent=2))
        print(json.dumps(results, indent=2))
        return


if __name__ == "__main__":
    main()


