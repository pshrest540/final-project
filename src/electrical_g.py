import pandas as pd
import numpy as np
from pathlib import Path

def generate_electrical_data(rows=5000):
    script_path   = Path(__file__).resolve()
    processed_path = script_path.parent.parent / "data" / "processed"
    processed_path.mkdir(parents=True, exist_ok=True)

    data = []
    CURRENT_YEAR = 2026

    for _ in range(rows):
        year       = np.random.randint(2000, 2025)
        mileage    = np.random.randint(500, 250000)
        temp_scale  = np.random.uniform(0, 1)
        habit_scale = np.random.uniform(0, 1)
        idle_scale  = np.random.uniform(0, 1)

        age = CURRENT_YEAR - year

        # FIX: battery was dying at ~7 years old (age * 10 = 100 at age 10)
        # Real batteries last 5-7 years but age penalty should be gradual
        # New formula floors battery around 15-20 years old under avg conditions
        bat_base = 100 - (age * 5)   - (temp_scale  * 20) - (mileage / 25000)
        alt_base = 100 - (mileage / 4000) - (idle_scale  * 15) - (temp_scale * 10)
        sta_base = 100 - (age * 2.5) - (habit_scale * 15) - (mileage / 15000)

        noise = np.random.normal(loc=0, scale=5, size=3)

        bat_wellness = bat_base + noise[0]
        alt_wellness = alt_base + noise[1]
        sta_wellness = sta_base + noise[2]

        # Rare sudden failure events (1% chance)
        if np.random.random() < 0.01:
            alt_wellness = np.random.uniform(5, 20)

        scores = [max(5, min(100, s)) for s in [bat_wellness, alt_wellness, sta_wellness]]

        data.append([year, mileage, round(temp_scale, 2), round(habit_scale, 2),
                     round(idle_scale, 2), round(scores[0], 2), round(scores[1], 2), round(scores[2], 2)])

    columns = ['year', 'mileage', 'temp_scale', 'habit_scale', 'idle_scale',
               'bat_wellness', 'alt_wellness', 'sta_wellness']

    df = pd.DataFrame(data, columns=columns)
    output_file = processed_path / "electrical_physics.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved electrical_physics.csv ({len(df)} rows)")
    print(df[['bat_wellness', 'alt_wellness', 'sta_wellness']].describe().round(1))


generate_electrical_data()
