import pandas as pd
import numpy as np
import os

def generate_drivetrain_physics():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    processed_dir = os.path.join(project_root, "data", "processed")

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        print(f"Created directory at: {processed_dir}")

    rows = 5000
    CURRENT_YEAR = 2026
    data = []

    for _ in range(rows):
        year    = np.random.randint(2000, 2025)
        mileage = np.random.randint(500, 250000)

        rough_road   = np.random.uniform(0, 1)
        torque_load  = np.random.uniform(0, 1)
        braking_freq = np.random.uniform(0, 1)

        # FIX: increased divisors so components don't floor until high mileage
        # cv joints realistically last 100k-150k miles
        # wheel bearings realistically last 100k-150k miles
        # brakes realistically last 50k-70k miles (was 45k — too low)
        cv_base  = 100 - (mileage / 3500) - (torque_load  * 15)
        wb_base  = 100 - (mileage / 4000) - (rough_road   * 15)
        brk_base = 100 - (mileage / 2500) - (braking_freq * 20)

        noise  = np.random.normal(0, 5, 3)
        scores = [max(5, min(100, s + n)) for s, n in zip([cv_base, wb_base, brk_base], noise)]

        data.append([year, mileage, round(rough_road, 2), round(torque_load, 2),
                     round(braking_freq, 2), *[round(s, 2) for s in scores]])

    columns = ['year', 'mileage', 'rough_scale', 'torque_scale', 'stop_scale',
               'cv_wellness', 'wb_wellness', 'brk_wellness']

    df = pd.DataFrame(data, columns=columns)
    output_file = os.path.join(processed_dir, "drivetrain_physics.csv")
    df.to_csv(output_file, index=False)
    print(f"Saved drivetrain_physics.csv ({len(df)} rows)")
    print(df[['cv_wellness', 'wb_wellness', 'brk_wellness']].describe().round(1))


generate_drivetrain_physics()
