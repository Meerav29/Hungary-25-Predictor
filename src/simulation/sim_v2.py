import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

YEAR = 2025
N_SIMULATIONS = 1000000

TEAM_COLORS = {
    'Red Bull': '#3671C6',
    'Mercedes': '#6CD3BF',
    'Ferrari': '#F91536',
    'McLaren': '#FF8000',
    'Aston Martin': '#229971',
    'Alpine': '#2293D1',
    'Williams': '#37BEDD',
    'RB': '#6692FF',           # ex-AlphaTauri, now “RB”
    'Haas': '#B6BABD',
    'Stake Sauber': '#52E252',       # Stake F1/Sauber
    # Add new teams here if needed!
}

def get_latest_race_round():
    schedule = fastf1.get_event_schedule(YEAR)
    today = pd.Timestamp.today(tz='Europe/Budapest').tz_localize(None)
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
        all_results.groupby(['Abbreviation', 'TeamName'])['AdjPosition']
        .mean()
        .reset_index()
        .rename(columns={'AdjPosition': 'AvgFinish'})
    )
    driver_perf['Score'] = 1 / driver_perf['AvgFinish']
    driver_perf['NormScore'] = (driver_perf['Score'] - driver_perf['Score'].min()) / (driver_perf['Score'].max() - driver_perf['Score'].min())
    return driver_perf

def get_latest_hungary_quali(year):
    schedule = fastf1.get_event_schedule(year)
    hun_row = schedule[schedule['EventName'].str.contains("Hungarian", case=False, na=False)].iloc[0]
    rnd = int(hun_row['RoundNumber'])
    session = fastf1.get_session(year, rnd, 'Qualifying')
    session.load()
    quali = session.results[['Abbreviation', 'TeamName', 'Position']].copy()
    quali['Position'] = quali['Position'].astype(int)
    quali = quali.sort_values('Position').reset_index(drop=True)
    return quali

def run_simulation(sim_df, n_sim=N_SIMULATIONS):
    sim_df['SimWins'] = 0
    for _ in range(n_sim):
        # Simulate possible DNFs: 2% DNF chance for each driver
        probs = sim_df['WinProb'].copy()
        dnf = np.random.rand(len(probs)) < 0.02  # 2% chance DNF
        probs[dnf] = 0
        if probs.sum() == 0:
            continue
        probs = probs / probs.sum()
        winner = np.random.choice(sim_df['Abbreviation'], p=probs)
        sim_df.loc[sim_df['Abbreviation'] == winner, 'SimWins'] += 1
    sim_df['SimWinPct'] = sim_df['SimWins'] / n_sim * 100
    return sim_df.sort_values('SimWinPct', ascending=False)

if __name__ == "__main__":
    print("Fetching 2025 race results...")
    latest_round = get_latest_race_round()
    print(f"Latest completed round: {latest_round}")
    driver_perf = get_driver_performance(YEAR, latest_round)
    print(driver_perf.sort_values('NormScore', ascending=False)[['Abbreviation', 'TeamName', 'AvgFinish', 'NormScore']])

    print("\nFetching Hungarian GP qualifying results...")
    quali = get_latest_hungary_quali(YEAR)
    print(quali)

    # Grid score
    max_pos = quali['Position'].max()
    quali['GridScore'] = 1 - (quali['Position'] - 1) / (max_pos - 1)

    # Merge performance into quali
    sim_df = quali.merge(driver_perf[['Abbreviation', 'NormScore']], on='Abbreviation', how='left')
    sim_df['NormScore'] = sim_df['NormScore'].fillna(sim_df['NormScore'].min())

    # Blend: Tune weights (0.7 perf, 0.3 grid)
    perf_wt = 0.7
    grid_wt = 0.3
    sim_df['FinalScore'] = perf_wt * sim_df['NormScore'] + grid_wt * sim_df['GridScore']
    sim_df['WinProb'] = sim_df['FinalScore'] / sim_df['FinalScore'].sum()

    sim_results = run_simulation(sim_df)

    print("\nHungarian GP 2025 Win Probabilities (Performance+Grid+Team Colors):")
    print(sim_results[['Abbreviation', 'TeamName', 'Position', 'SimWinPct']])

    # Plot with F1 team colors!
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(13, 7))

    # Use team colors for each bar
    colors = [TEAM_COLORS.get(team, "#222222") for team in sim_results['TeamName']]
    bars = ax.bar(sim_results['Abbreviation'], sim_results['SimWinPct'], color=colors, edgecolor="black", width=0.6)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points", ha='center', va='bottom',
                    fontsize=13, fontweight='bold')

    # Modern F1 Title
    ax.set_title("🏁 2025 Hungarian GP – Win Probability Simulation", fontsize=22, fontweight='bold', loc='left', pad=20)
    ax.set_ylabel("Win Probability (%)", fontsize=16)
    ax.set_xlabel("Driver", fontsize=14)
    plt.xticks(fontsize=13, fontweight='bold')
    plt.yticks(fontsize=13)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())

    # Remove right and top borders, keep gridlines light
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', color='gray', linestyle='dashed', linewidth=0.7, alpha=0.5)

    # Optional: legend for teams
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=color, label=team) for team, color in TEAM_COLORS.items()]
    plt.legend(handles=handles, title='Teams', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)

    # Caption or watermark (optional)
    plt.figtext(0.99, 0.01, "meerav.dev | F1 Simulations", ha="right", fontsize=11, color="gray", alpha=0.7)

    plt.tight_layout()
    plt.savefig("hungary2025_win_probs_teamcolors.png", dpi=300, bbox_inches='tight')
    plt.show()
