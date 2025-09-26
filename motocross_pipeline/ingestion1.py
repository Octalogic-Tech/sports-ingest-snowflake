import requests
import json
import snowflake.connector
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Snowflake connection parameters
conn_params = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'role': os.getenv('SNOWFLAKE_ROLE')
}

# API endpoints
API_KEY = "9981aae9-7668-46a1-a0d6-b03efa26bb90"
EVENT_URL = "https://results.supermotocross.com/results?p=view_event&export=json&key={}&id={}"
RESULTS_URL = "https://results.supermotocross.com/results?p=view_race_result&export=json&key={}&id={}"
EVENTS_PAGE = "https://results.supermotocross.com/events/"

def scrape_event_ids():
    """Scrape event IDs from the events page"""
    print(f"Scraping events page: {EVENTS_PAGE}")
    resp = requests.get(EVENTS_PAGE)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    event_ids = []
    for link in soup.find_all('a', href=True):
        if "view_event&id=" in link['href']:
            try:
                event_id = link['href'].split("id=")[-1]
                if event_id.isdigit() and event_id not in event_ids:
                    event_ids.append(event_id)
            except Exception:
                continue
    print(f"✅ Found {len(event_ids)} event IDs.")
    return event_ids

def fetch_api_data(url):
    """Fetch data from API endpoint"""
    print(f"Fetching: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_race_ids_from_event_payload(event_payload):
    """Extract race/result IDs from various possible event JSON shapes."""
    race_ids = []
    try:
        data = event_payload.get("data", {}) if isinstance(event_payload, dict) else {}
        event_obj = data.get("event", {}) if isinstance(data, dict) else {}

        # Shape 1: data.event.races -> list of objects with id
        races = event_obj.get("races", []) if isinstance(event_obj, dict) else []
        for r in races or []:
            rid = (r.get("id") if isinstance(r, dict) else None) or (r.get("result_id") if isinstance(r, dict) else None) or (r.get("race_id") if isinstance(r, dict) else None)
            if rid is not None:
                race_ids.append(str(rid))

        # Shape 2: data.event.classes[*].races[*].id
        classes = event_obj.get("classes", []) if isinstance(event_obj, dict) else []
        for cls in classes or []:
            for r in (cls.get("races", []) if isinstance(cls, dict) else []) or []:
                rid = (r.get("id") if isinstance(r, dict) else None) or (r.get("result_id") if isinstance(r, dict) else None) or (r.get("race_id") if isinstance(r, dict) else None)
                if rid is not None:
                    race_ids.append(str(rid))

        # Shape 3: data.races at root
        root_races = data.get("races", []) if isinstance(data, dict) else []
        for r in root_races or []:
            rid = (r.get("id") if isinstance(r, dict) else None) or (r.get("result_id") if isinstance(r, dict) else None) or (r.get("race_id") if isinstance(r, dict) else None)
            if rid is not None:
                race_ids.append(str(rid))

        # Deduplicate and keep only digit ids
        race_ids = [rid for rid in {str(rid) for rid in race_ids} if rid.isdigit()]
        return race_ids
    except Exception:
        return []

def scrape_race_ids_from_event_page(event_id):
    """Fallback: scrape race result IDs from the event HTML page."""
    url = f"https://results.supermotocross.com/results?p=view_event&id={event_id}"
    print(f"Scraping race IDs from HTML: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    race_ids = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "view_race_result&id=" in href:
            try:
                rid = href.split("id=")[-1]
                if rid.isdigit():
                    race_ids.append(rid)
            except Exception:
                continue
    race_ids = list({rid for rid in race_ids})
    print(f"Found {len(race_ids)} race IDs from HTML for event {event_id}")
    return race_ids

def merge_to_snowflake(conn, table_name, id_value, payload):
    """UPSERT JSON data into Snowflake table by ID"""
    cursor = conn.cursor()
    payload_json = json.dumps(payload)

    sql = f"""
        MERGE INTO {table_name} t
        USING (SELECT %s AS id, PARSE_JSON(%s) AS payload) s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE 
            SET payload = s.payload, pulled_at = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN 
            INSERT (id, payload) VALUES (s.id, s.payload)
    """
    cursor.execute(sql, (id_value, payload_json))
    cursor.close()
    print(f"⬆️ Upserted into {table_name}: {id_value}")

def merge_race_result_with_event(conn, table_name, result_id, event_id, payload):
    """Upsert race result JSON with linkage to its event_id."""
    cursor = conn.cursor()
    payload_json = json.dumps(payload)

    sql = f"""
        MERGE INTO {table_name} t
        USING (SELECT %s AS id, %s AS event_id, PARSE_JSON(%s) AS payload) s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE 
            SET payload = s.payload, event_id = s.event_id, pulled_at = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN 
            INSERT (id, event_id, payload) VALUES (s.id, s.event_id, s.payload)
    """
    cursor.execute(sql, (result_id, event_id, payload_json))
    cursor.close()
    print(f"⬆️ Upserted into {table_name}: result {result_id} (event {event_id})")

def main():
    print("Connecting to Snowflake...")
    conn = snowflake.connector.connect(**conn_params)

    try:
        # Step 1: Scrape all event IDs
        event_ids = scrape_event_ids()

        for event_id in event_ids:
            # Fetch event details
            event_url = EVENT_URL.format(API_KEY, event_id)
            event_data = fetch_api_data(event_url)

            # UPSERT into EVENT_DETAILS
            merge_to_snowflake(conn, "RAW.EVENT_DETAILS", event_id, event_data)

            # Step 2: Extract race IDs robustly from payload; fallback to HTML scrape
            race_ids = extract_race_ids_from_event_payload(event_data)
            if not race_ids:
                print(f"No race IDs in payload for event {event_id}; trying HTML scrape...")
                race_ids = scrape_race_ids_from_event_page(event_id)
            if not race_ids:
                print(f"⚠️ No races found for event {event_id}")
                continue

            for result_id in race_ids:
                results_url = RESULTS_URL.format(API_KEY, result_id)
                result_data = fetch_api_data(results_url)
                # UPSERT into RACE_RESULTS with event linkage
                merge_race_result_with_event(conn, "RAW.RACE_RESULTS", result_id, event_id, result_data)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
        print("❄️ Snowflake connection closed")

if __name__ == "__main__":
    main()