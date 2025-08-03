import fastf1
import pandas as pd
import numpy as np

YEAR = 2025
N_SIMULATIONS = 10000

def get_latest_race_round():
    schedule = fastf1.get_event_schedule(YEAR)
    today = pd.Timestamp.today(tz='Europe/Budapest').tz_localize(None)  # FIXED
    completed = schedule[schedule['EventDate'] < today]
    return completed['RoundNumber'].max()

def get_driver_performance(year, upto_round):
    results_list = []
    for rnd in range(1, upto_round+1):
        try:
            session = fastf1.get_session(year, rnd, 'Race')
            session.load()
            df = session.results[['Abbreviation', 'TeamName', 'Position', 'Status']]
            df['Round'] = rnd
            results_list.append(df)
        except Exception as e:
            print(f"Could not load round {rnd}: {e}")
    if not results_list:
        raise Exception("No race results loaded!")
    all_results = pd.concat(results_list, ignore_index=True)
    all_results['AdjPosition'] = all_results.apply(
        lambda row: row['Position'] if row['Status'] == 'Finished' else 20, axis=1
    )
    driver_perf = (
        all_results.groupby('Abbreviation')['AdjPosition']
        .mean()
        .reset_index()
        .rename(columns={'AdjPosition': 'AvgFinish'})
    )
    # Invert & normalize so higher = better
    driver_perf['Score'] = 1 / driver_perf['AvgFinish']
    driver_perf['NormScore'] = (driver_perf['Score'] - driver_perf['Score'].min()) / (driver_perf['Score'].max() - driver_perf['Score'].min())
    return driver_perf

def get_latest_hungary_quali(year):
    # Find Hungary event
    schedule = fastf1.get_event_schedule(year)
    hun_row = schedule[schedule['EventName'].str.contains("Hungarian", case=False, na=False)].iloc[0]
    rnd = int(hun_row['RoundNumber'])
    session = fastf1.get_session(year, rnd, 'Qualifying')
    session.load()
    quali = session.results[['Abbreviation', 'Position']].copy()
    quali['Position'] = quali['Position'].astype(int)
    quali = quali.sort_values('Position').reset_index(drop=True)
    return quali

def run_simulation(quali, driver_perf, n_sim=N_SIMULATIONS):
    # Merge driver performance score with quali
    sim_df = quali.merge(driver_perf[['Abbreviation', 'NormScore']], on='Abbreviation', how='left')
    # If NormScore is missing (e.g., reserve driver), fill with min value
    sim_df['NormScore'] = sim_df['NormScore'].fillna(sim_df['NormScore'].min())

    # Probabilities strictly from driver performance this year
    sim_df['WinProb'] = sim_df['NormScore'] / sim_df['NormScore'].sum()
    sim_df['SimWins'] = 0

    for _ in range(n_sim):
        winner = np.random.choice(sim_df['Abbreviation'], p=sim_df['WinProb'])
        sim_df.loc[sim_df['Abbreviation'] == winner, 'SimWins'] += 1

    sim_df['SimWinPct'] = sim_df['SimWins'] / n_sim * 100
    return sim_df.sort_values('SimWinPct', ascending=False)

if __name__ == "__main__":
    print("Fetching 2025 race results...")
    latest_round = get_latest_race_round()
    print(f"Latest completed round: {latest_round}")
    driver_perf = get_driver_performance(YEAR, latest_round)
    print(driver_perf.sort_values('NormScore', ascending=False)[['Abbreviation', 'AvgFinish', 'NormScore']])

    print("\nFetching Hungarian GP qualifying results...")
    quali = get_latest_hungary_quali(YEAR)
    print(quali)

    print("\nRunning win probability simulation (this year only, 100% performance-based)...")
    sim_results = run_simulation(quali, driver_perf)
    print("\nHungarian GP 2025 Win Probabilities (Performance-Based):")
    print(sim_results[['Abbreviation', 'Position', 'SimWinPct']])
