import json
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────
random.seed(42)

CARRIERS = [
    {"code": "AA", "name": "American Airlines", "alliance": "OneWorld"},
    {"code": "DL", "name": "Delta Air Lines",   "alliance": "SkyTeam"},
    {"code": "UA", "name": "United Airlines",   "alliance": "StarAlliance"},
    {"code": "SW", "name": "Southwest Airlines","alliance": "None"},
    {"code": "B6", "name": "JetBlue Airways",   "alliance": "None"},
]

AIRPORTS = [
    {"code": "JFK", "name": "John F Kennedy International", "city": "New York",    "state": "NY", "region": "Northeast", "runways": 4},
    {"code": "LAX", "name": "Los Angeles International",    "city": "Los Angeles", "state": "CA", "region": "West",      "runways": 4},
    {"code": "ORD", "name": "OHare International",          "city": "Chicago",     "state": "IL", "region": "Midwest",   "runways": 8},
    {"code": "ATL", "name": "Hartsfield Jackson Atlanta",   "city": "Atlanta",     "state": "GA", "region": "South",     "runways": 5},
    {"code": "DFW", "name": "Dallas Fort Worth",            "city": "Dallas",      "state": "TX", "region": "South",     "runways": 7},
    {"code": "SFO", "name": "San Francisco International",  "city": "San Francisco","state":"CA", "region": "West",      "runways": 4},
    {"code": "MIA", "name": "Miami International",          "city": "Miami",       "state": "FL", "region": "South",     "runways": 4},
    {"code": "SEA", "name": "Seattle Tacoma International", "city": "Seattle",     "state": "WA", "region": "Northwest", "runways": 3},
    {"code": "BOS", "name": "Logan International",          "city": "Boston",      "state": "MA", "region": "Northeast", "runways": 4},
    {"code": "DEN", "name": "Denver International",         "city": "Denver",      "state": "CO", "region": "West",      "runways": 6},
]

DELAY_REASONS = ["WEATHER", "ATC", "CARRIER", "SECURITY", "NAS"]
WEATHER_CONDITIONS = ["Heavy fog", "Thunderstorm", "Snow storm", "High winds", "Ice on runway", "Low visibility"]
EVENTS = ["GATE_OPEN", "BOARDING_START", "BOARDING_COMPLETE", "DOOR_CLOSED", "PUSHBACK", "AIRBORNE"]

# ── Helper ────────────────────────────────────────────────────────
def random_date(start_year=2024):
    start = datetime(start_year, 1, 1)
    delta = timedelta(days=random.randint(0, 364),
                      hours=random.randint(0, 23),
                      minutes=random.randint(0, 59))
    return start + delta

# ── 1. flights_api_response.json (Nested JSON) ────────────────────
print("Generating flights_api_response.json ...")
flights = []
for i in range(5000):
    carrier  = random.choice(CARRIERS)
    origin   = random.choice(AIRPORTS)
    dest     = random.choice([a for a in AIRPORTS if a["code"] != origin["code"]])
    dep_time = random_date()
    arr_time = dep_time + timedelta(hours=random.randint(1, 8))
    dep_delay = random.randint(-10, 120)
    arr_delay = dep_delay + random.randint(-15, 15)
    cancelled = random.random() < 0.03

    flight = {
        "flight_id": f"{carrier['code']}-{dep_time.strftime('%Y%m%d')}-{str(i).zfill(4)}",
        "schedule": {
            "departure": {
                "airport":  origin["code"],
                "time":     dep_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "terminal": random.choice(["A", "B", "C", "D"])
            },
            "arrival": {
                "airport":  dest["code"],
                "time":     arr_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "terminal": random.choice(["1", "2", "3", "4"])
            }
        },
        "carrier": carrier,
        "performance": {
            "dep_delay_mins": dep_delay,
            "arr_delay_mins": arr_delay,
            "cancelled":      cancelled,
            "diverted":       random.random() < 0.01
        },
        "delay_reasons":   random.sample(DELAY_REASONS, k=random.randint(0, 2)),
        "passenger_count": random.randint(80, 220)
    }
    flights.append(flight)

with open("data/raw/flights_api_response.json", "w") as f:
    json.dump(flights, f, indent=2)
print(f"  Done — {len(flights)} flights written")

# ── 2. weather_reports.txt (Free Text) ───────────────────────────
print("Generating weather_reports.txt ...")
weather_lines = []
for i in range(1000):
    carrier   = random.choice(CARRIERS)
    airport   = random.choice(AIRPORTS)
    condition = random.choice(WEATHER_CONDITIONS)
    date      = random_date()
    delay_min = random.randint(15, 180)
    flt_num   = f"{carrier['code']}{random.randint(100, 999)}"

    line = (
        f"FLT {flt_num} {airport['code']} {date.strftime('%Y-%m-%d')}: "
        f"{condition} reported at origin. "
        f"Delay of {delay_min} minutes attributed to weather conditions. "
        f"Ground stop issued {date.strftime('%H%M')}-{(date + timedelta(minutes=delay_min)).strftime('%H%M')} local time."
    )
    weather_lines.append(line)

with open("data/raw/weather_reports.txt", "w") as f:
    f.write("\n\n".join(weather_lines))
print(f"  Done — {len(weather_lines)} weather reports written")

# ── 3. airline_events_log.json (Array JSON) ───────────────────────
print("Generating airline_events_log.json ...")
event_logs = []
for i in range(3000):
    carrier  = random.choice(CARRIERS)
    date     = random_date()
    flt_id   = f"{carrier['code']}-{date.strftime('%Y%m%d')}-{str(i).zfill(4)}"
    t        = date
    events   = []
    for evt in EVENTS:
        events.append({
            "timestamp": t.strftime("%H:%M"),
            "event":     evt,
            "status":    random.choice(["ON_TIME", "DELAYED", "DELAYED"])
        })
        t += timedelta(minutes=random.randint(5, 25))

    event_logs.append({"flight_id": flt_id, "events": events})

with open("data/raw/airline_events_log.json", "w") as f:
    json.dump(event_logs, f, indent=2)
print(f"  Done — {len(event_logs)} event logs written")

# ── 4. airport_master.xml (XML) ───────────────────────────────────
print("Generating airport_master.xml ...")
root = ET.Element("airports")
for ap in AIRPORTS:
    node = ET.SubElement(root, "airport", code=ap["code"])
    ET.SubElement(node, "name").text     = ap["name"]
    ET.SubElement(node, "city").text     = ap["city"]
    ET.SubElement(node, "state").text    = ap["state"]
    ET.SubElement(node, "region").text   = ap["region"]
    ET.SubElement(node, "runways").text  = str(ap["runways"])

tree = ET.ElementTree(root)
ET.indent(tree, space="  ")
tree.write("data/raw/airport_master.xml",
           encoding="unicode",
           xml_declaration=True)
print(f"  Done — {len(AIRPORTS)} airports written")

print("\n✅ All 4 source files generated in data/raw/")