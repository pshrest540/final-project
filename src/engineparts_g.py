import pandas as pd
import numpy as np
import os

def generate_engine_cooling_physics():
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    processed_dir = os.path.join(project_root, "data", "processed")

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    rows = 5000
    CURRENT_YEAR = 2026
    data = []

    for _ in range(rows):
        year    = np.random.randint(2000, 2025)
        mileage = np.random.randint(500, 250000)

        temp_env    = np.random.uniform(0, 1)
        idle_scale  = np.random.uniform(0, 1)
        habit_scale = np.random.uniform(0, 1)

        age = CURRENT_YEAR - year

        # FIX: coolant was flooring at ~14 years (age * 4.5 = 63 at age 14)
        # Real coolant systems last much longer with maintenance
        # Ignition (spark plugs) realistically last 60k-100k miles
        # Fuel pump realistically lasts 100k-150k miles
        coolant_base  = 100 - (age * 2.5)   - (temp_env   * 20) - (idle_scale * 10) - (mileage / 6000)
        ignition_base = 100 - (mileage / 3000) - (habit_scale * 12)
        fuel_base     = 100 - (mileage / 5000) - (temp_env   * 10)

        noise = np.random.normal(0, 5, 3)
        rad_w  = coolant_base  + noise[0]
        ign_w  = ignition_base + noise[1]
        fuel_w = fuel_base     + noise[2]

        # Rare sudden failure event (1% chance)
        if np.random.random() < 0.01:
            rad_w = np.random.uniform(5, 15)

        scores = [max(5, min(100, s)) for s in [rad_w, ign_w, fuel_w]]

        data.append([
            year, mileage,
            round(temp_env, 2), round(idle_scale, 2), round(habit_scale, 2),
            round(scores[0], 2), round(scores[1], 2), round(scores[2], 2)
        ])

    columns = ['year', 'mileage', 'temp_scale', 'idle_scale', 'habit_scale',
               'coolant_wellness', 'ignition_wellness', 'fuel_wellness']

    df = pd.DataFrame(data, columns=columns)
    output_file = os.path.join(processed_dir, "engine_physics.csv")
    df.to_csv(output_file, index=False)
    print(f"Saved engine_physics.csv ({len(df)} rows)")
    print(df[['coolant_wellness', 'ignition_wellness', 'fuel_wellness']].describe().round(1))


generate_engine_cooling_physics()
