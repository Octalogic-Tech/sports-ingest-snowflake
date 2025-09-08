import requests
import json

def fetch_results():
    print("Fetching results from API...")

    url = "https://results.supermotocross.com/results?p=view_race_result&export=json&key=9981aae9-7668-46a1-a0d6-b03efa26bb90&id=5886759"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch results. Status code: {response.status_code}")
        return

    data = response.json()

    print("\nAPI Response received. Top-level keys:")
    print(list(data.keys()))

    if "race" in data:
        race = data["race"]
        print("\n'race' object keys:")
        print(list(race.keys()))

        if "drivers" in race:
            drivers = race["drivers"]

            if isinstance(drivers, dict):
                print(f"\nFound {len(drivers)} drivers (dict format)")

                # Get first key
                first_key = list(drivers.keys())[0]
                first_driver = drivers[first_key]

                print("\n Example driver entry (first one):")
                print(json.dumps(first_driver, indent=2))

                # Print just names + positions
                print("\nDriver Positions:")
                for k, d in drivers.items():
                    print(f"Position {d.get('position')} - {d.get('name_display')}")
            elif isinstance(drivers, list):
                print(f"\nFound {len(drivers)} drivers (list format)")

                print("\ Example driver entry (first one):")
                print(json.dumps(drivers[0], indent=2))

                print("\n Driver Positions:")
                for d in drivers:
                    print(f"Position {d.get('position')} - {d.get('name_display')}")
            else:
                print("\ Unknown 'drivers' format")

        else:
            print("\nNo 'drivers' field found inside race")

    else:
        print(" No 'race' field in response")


if __name__ == "__main__":
    fetch_results()
