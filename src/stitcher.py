import pandas as pd
import numpy as np
import os
from pathlib import Path

def load_and_stitch():
 
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    raw_path = project_root / "data" / "raw"
    processed_path = project_root / "data" / "processed"

  

  
    try:
        servicerecords = pd.read_csv(raw_path / 'ServiceRecords.csv')
        Emain = pd.read_csv(raw_path / 'Emaintainance.csv')
        diagnostic = pd.read_csv(raw_path / 'diagnostic.csv')
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"Make sure your CSVs are in: {raw_path}")
        return


    emain_stress = Emain.groupby('Maintenance_Type').agg({
        'Battery_Voltage': 'std',
        'Battery_Temperature': 'mean',
        'Motor_RPM': 'mean',
        'Idle_Time': 'mean'
    }).rename(columns={
        'Battery_Voltage': 'volt_fluctuation',
        'Battery_Temperature': 'avg_temp',
        'Motor_RPM': 'avg_rpm',
        'Idle_Time': 'avg_idle'
    }).reset_index()


    brand_boost = {
        'toyota': 1.15, 'lexus': 1.15, 'honda': 1.10, 'subaru': 1.10, 
        'mazda': 1.10, 'bmw': 1.05, 'buick': 1.05, 'ford': 1.00, 
        'chevrolet': 1.00, 'nissan': 0.95, 'hyundai': 0.95, 'kia': 0.95
    }

    parts_baseline = {
        'alternator': 160000, 'battery': 150000, 'starter_motor': 150000, 
        'serpentine_belt': 100000, 'ignition_coils': 130000, 'cv_axle': 140000, 
        'wheel_bearings': 160000, 'fuel_pump': 160000, 'clutch': 110000, 
        'bushings': 100000, 'brake_pads': 50000, 'radiator': 200000, 
        'water_pump': 120000, 'spark_plugs': 80000, 'o2_sensor': 120000
    }


    def calculate_wellness(row):
        scores = {}
        brand = str(row.get('brand', '')).lower().strip()
        multiplier = brand_boost.get(brand, 1.0)
        
       
        env_penalty = 0.9 if row.get('region', '').lower() == 'chennai' else 1.0
        
      
        sensor_stress = 1.0
        
        if 'avg_temp' in row and row['avg_temp'] > 40:
            sensor_stress *= 0.95

        for part, baseline in parts_baseline.items():
            mileage = row.get('mileage', 0)
            
        
            health = (1 - (mileage / (baseline * multiplier))) * 100
            
          
            health = health * env_penalty * sensor_stress
            
            scores[f'{part}_wellness'] = max(0, min(100, health))
        
        return pd.Series(scores)

    
    servicerecords['Maintenance_Type'] = 1 
    merged_df = pd.merge(servicerecords, emain_stress, on='Maintenance_Type', how='left')


    wellness_results = merged_df.apply(calculate_wellness, axis=1)
    final_dataset = pd.concat([merged_df, wellness_results], axis=1)

  
    os.makedirs(processed_path, exist_ok=True)
    final_dataset.to_csv(processed_path / 'perfect_dataset_vfinal.csv', index=False)
    
    print(f"✨ SUCCESS: 'perfect_dataset_vfinal.csv' created in {processed_path}")
    print(f"📊 Total Rows Processed: {len(final_dataset)}")


load_and_stitch()