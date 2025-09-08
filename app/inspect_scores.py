from database import SessionLocal
from models import Scores
import json

def inspect_scores_metric_value(session):
    print("\nChecking Scores.metric_value fields...")

    scores = session.query(Scores).limit(20).all()  
    for s in scores:
        try:
            if s.metric_value:
                print(f"\nScore ID: {s.id}")
                print(json.dumps(s.metric_value, indent=2)) 
            else:
                print(f"Score {s.id}: (no metric_value)")
        except Exception as ex:
            print(f"Score {s.id}: error parsing metric_value → {ex}")

if __name__ == "__main__":
    session = SessionLocal()
    try:
        inspect_scores_metric_value(session)
    finally:
        session.close()
