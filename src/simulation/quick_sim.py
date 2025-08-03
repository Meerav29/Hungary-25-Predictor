import fastf1
import numpy as np
import pandas as pd

# CONFIG
YEAR = 2025
ROUND = 'Hungary'  # Or actual round number if needed
N_SIMULATIONS = 10000

# 1. Get qualifying results for Hungary 2025
session = fastf1.get_session(YEAR, ROUND, 'Qualifying')
session.load()
quali = session.results[['DriverNumber', 'Abbreviation', 'Position']].copy()
quali['Position'] = quali['Position'].astype(int)
quali = quali.sort_values('Position').reset_index(drop=True)

# 2. Assign base win probabilities by grid position
# (Simple: 1st = 25%, 2nd = 20%, ..., 10th+ = small)
base_probs = [0.25, 0.20, 0.15, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03, 0.02]
probs = [base_probs[p-1] if p <= len(base_probs) else 0.01 for p in quali['Position']]
quali['WinProb'] = probs
quali['SimWins'] = 0

# 3. Run Monte Carlo simulation
drivers = quali['Abbreviation'].values
driver_probs = quali['WinProb'].values

for _ in range(N_SIMULATIONS):
    winner = np.random.choice(drivers, p=driver_probs/np.sum(driver_probs))
    quali.loc[quali['Abbreviation'] == winner, 'SimWins'] += 1

quali['SimWinPct'] = quali['SimWins'] / N_SIMULATIONS * 100

# 4. Show results
print("Hungarian GP 2025 - Win Probability Simulation Results:")
print(quali[['Abbreviation', 'Position', 'SimWinPct']].sort_values('SimWinPct', ascending=False))

# Optional: Plot
import matplotlib.pyplot as plt
plt.bar(quali['Abbreviation'], quali['SimWinPct'])
plt.ylabel("Win Probability (%)")
plt.title("Simulated Win Odds - Hungarian GP 2025")
plt.show()
