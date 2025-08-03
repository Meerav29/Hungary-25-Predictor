import fastf1
import pandas as pd
import os
from fastf1 import events

# --- Config ---
START_YEAR = 2018
END_YEAR = 2024  
SESSIONS = ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race']
RAW_DATA_DIR = 'data/raw/'

os.makedirs(RAW_DATA_DIR, exist_ok=True)

def get_hungary_event(year):
    event_schedule = fastf1.get_event_schedule(year)
    # Find the Hungarian Grand Prix row
    for _, row in event_schedule.iterrows():
        if 'Hungarian' in row['EventName']:
            return row
    return None

def fetch_and_save_session(year, session_name):
    event = get_hungary_event(year)
    if event is None:
        print(f"[{year}] Hungarian GP not found.")
        return

    gp_round = int(event['RoundNumber'])

    try:
        session = fastf1.get_session(year, gp_round, session_name)
        session.load()
        print(f"[{year}] {session_name}: Loaded.")
    except Exception as e:
        print(f"[{year}] {session_name}: Error loading session: {e}")
        return

    # --- Save race results ---
    if session_name == 'Race':
        results = session.results
        if results is not None:
            results.to_csv(f"{RAW_DATA_DIR}{year}_hungary_race_results.csv", index=False)
        else:
            print(f"[{year}] Race results not found.")

    # --- Save lap times ---
    try:
        laps = session.laps
        if laps is not None and not laps.empty:
            laps.to_csv(f"{RAW_DATA_DIR}{year}_hungary_{session_name.lower().replace(' ', '')}_laps.csv", index=False)
    except Exception as e:
        print(f"[{year}] {session_name}: No laps data ({e})")

    # --- Save weather data ---
    try:
        weather = session.weather_data
        if weather is not None and not weather.empty:
            weather.to_csv(f"{RAW_DATA_DIR}{year}_hungary_{session_name.lower().replace(' ', '')}_weather.csv", index=False)
    except Exception as e:
        print(f"[{year}] {session_name}: No weather data ({e})")

if __name__ == "__main__":
    for year in range(START_YEAR, END_YEAR + 1):
        for session_name in SESSIONS:
            fetch_and_save_session(year, session_name)
