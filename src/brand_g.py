import pandas as pd
import os

def add_brand_to_reliability(brand_name, model_data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    processed_dir = os.path.join(project_root, "data", "processed")
    file_path = os.path.join(processed_dir, "brand_model_reliability.csv")

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    new_df = pd.DataFrame(model_data, columns=[
        'brand', 'model', 'type', 'elec_score', 'drive_score', 'engine_score'
    ])

    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        existing_df = existing_df[existing_df['brand'] != brand_name]
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(file_path, index=False)
    else:
        new_df.to_csv(file_path, index=False)


# ── Scoring guide (1-10 per system) ───────────────────────────────────────────
# Sources: Consumer Reports 2024-2026 reliability rankings, JD Power 2024-2025 VDS
#
# elec_score  : electrical system reliability (battery, alternator, starter, wiring)
# drive_score : drivetrain reliability (transmission, CV joints, wheel bearings, brakes)
# engine_score: engine reliability (cooling, ignition, fuel system, oil consumption)
#
# Scale: 10 = best in class | 7-8 = above average | 5-6 = average | 3-4 = below average | 1-2 = poor

full_market_data = {

    # ── TOYOTA ────────────────────────────────────────────────────────────────
    # CR 2026: #1 brand (score 66). JD Power 2024: #1 mass market.
    # Camry, Corolla, Tacoma, 4Runner all JD Power segment award winners.
    'Toyota': [
        # Corolla: one of the most reliable cars ever made, all systems excellent
        ['Toyota', 'Corolla',  'Sedan', 9, 9, 10],
        # Camry: JD Power segment winner, very strong engine, solid drivetrain
        ['Toyota', 'Camry',    'Sedan', 8, 9, 9],
        # RAV4: above average across the board, minor electrical gremlins on newer trims
        ['Toyota', 'RAV4',     'SUV',   8, 8, 9],
        # 4Runner: legendary drivetrain and engine, older electrical architecture
        ['Toyota', '4Runner',  'SUV',   7, 10, 9],
        # Tacoma: JD Power segment winner, bulletproof drivetrain and engine
        ['Toyota', 'Tacoma',   'Truck', 8, 9, 9],
    ],

    # ── HONDA ─────────────────────────────────────────────────────────────────
    # CR 2026: #4 brand (score 59). Reliable but had some recent connecting rod/bearing issues.
    # Generally strong engines, some CVT and electrical concerns on select models.
    'Honda': [
        # Civic: one of Honda's strongest, excellent all-round reliability
        ['Honda', 'Civic',     'Sedan', 8, 8, 9],
        # Accord: great engine, but CVT versions have had transmission concerns
        ['Honda', 'Accord',    'Sedan', 8, 7, 9],
        # CR-V: strong hybrid, ICE versions above average, minor electrical issues
        ['Honda', 'CR-V',      'SUV',   8, 8, 8],
        # Pilot: 9-speed transmission has had some reported issues, engine solid
        ['Honda', 'Pilot',     'SUV',   7, 6, 8],
        # Ridgeline: unique unibody truck, electrical above average for a truck
        ['Honda', 'Ridgeline', 'Truck', 8, 7, 8],
    ],

    # ── SUBARU ────────────────────────────────────────────────────────────────
    # CR 2025-2026: #1-2 brand overall. Known for conservative redesigns.
    # Weakness: boxer engine oil consumption on older models, CVT longevity concerns.
    'Subaru': [
        # Forester: CR top scorer, reliable across all systems
        ['Subaru', 'Forester',   'SUV',   8, 7, 7],
        # Outback: above average, CVT is the main concern for drivetrain
        ['Subaru', 'Outback',    'SUV',   7, 6, 7],
        # Crosstrek: shares reliable Forester components, strong overall
        ['Subaru', 'Crosstrek',  'SUV',   8, 7, 8],
        # Impreza: CR top scorer, very consistent reliability
        ['Subaru', 'Impreza',    'Sedan', 8, 7, 8],
        # WRX: performance-tuned engine runs harder, higher wear rate
        ['Subaru', 'WRX',        'Sedan', 7, 6, 6],
        # Ascent: 3-row CVT, some issues reported — weakest in lineup
        ['Subaru', 'Ascent',     'SUV',   6, 5, 6],
    ],

    # ── NISSAN ────────────────────────────────────────────────────────────────
    # CR 2026: #6 brand (score 57). JD Power mid-pack.
    # CVT transmission is the biggest reliability concern across many models.
    # Frontier and Pathfinder V6 are the strongest in the lineup.
    'Nissan': [
        # Frontier: body-on-frame with proven V6, no CVT — most reliable Nissan
        ['Nissan', 'Frontier',   'Truck', 7, 9, 9],
        # Pathfinder: V6 is solid, 9-speed auto better than CVT
        ['Nissan', 'Pathfinder', 'SUV',   7, 7, 8],
        # Altima: CVT concerns drag down drive score significantly
        ['Nissan', 'Altima',     'Sedan', 7, 4, 7],
        # Sentra: CVT also used here, smaller and cheaper to fix
        ['Nissan', 'Sentra',     'Sedan', 7, 5, 7],
        # Rogue: CVT history hurts, newer models improving but still below avg
        ['Nissan', 'Rogue',      'SUV',   6, 5, 6],
    ],

    # ── BMW ───────────────────────────────────────────────────────────────────
    # CR 2026: #2 in owner satisfaction, but reliability is mixed.
    # JD Power 2024: 190 PP100 (industry average), 3rd among premium brands.
    # Strong engines when maintained. Electrical/electronics are the weak point.
    # Expensive to repair when things go wrong.
    'BMW': [
        # 3 Series: sporty, well-engineered engine, complex electronics
        ['BMW', '3 Series', 'Sedan', 4, 7, 7],
        # 5 Series: more complex, more electrical systems, similar engine quality
        ['BMW', '5 Series', 'Sedan', 4, 6, 7],
        # X3: JD Power segment winner 2024, better than expected reliability
        ['BMW', 'X3',       'SUV',   5, 7, 7],
        # X5: complex PHEV variants drag down scores, ICE version above avg engine
        ['BMW', 'X5',       'SUV',   3, 6, 6],
        # 7 Series: flagship with maximum complexity, most electrical issues
        ['BMW', '7 Series', 'Sedan', 2, 5, 6],
    ],

    # ── FORD ──────────────────────────────────────────────────────────────────
    # CR 2026: #11 brand (score 48). JD Power mid-to-lower pack.
    # F-150 Hybrid improved. Mustang is a standout. Explorer and EcoSport are weak.
    'Ford': [
        # F-150 (non-hybrid): strong drivetrain, electrical more complex on newer
        ['Ford', 'F-150',    'Truck', 6, 8, 7],
        # Mustang: CR "well above average", strong engine, simpler than most Fords
        ['Ford', 'Mustang',  'Coupe', 7, 7, 8],
        # Explorer: historically problematic transmission and electrical
        ['Ford', 'Explorer', 'SUV',   4, 5, 5],
        # Focus: discontinued in US but drive score reflects the dual-clutch issues
        ['Ford', 'Focus',    'Sedan', 6, 4, 6],
        # EcoSport: one of CR's lowest-rated — poor across all systems
        ['Ford', 'EcoSport', 'SUV',   4, 4, 3],
    ],

    # ── CHEVROLET ─────────────────────────────────────────────────────────────
    # CR 2026: #17 brand (score 42). Some standouts but inconsistent lineup.
    # Corvette and Trax score above average. Blazer EV and redesigned models weak.
    'Chevrolet': [
        # Silverado: workhorse truck, drivetrain strong, electrical average
        ['Chevrolet', 'Silverado', 'Truck', 5, 7, 6],
        # Tahoe: JD Power segment winner, stronger than typical Chevy
        ['Chevrolet', 'Tahoe',     'SUV',   6, 7, 6],
        # Trax: CR above average, small and simple = more reliable
        ['Chevrolet', 'Trax',      'SUV',   6, 6, 6],
        # Malibu: average reliability, nothing exceptional
        ['Chevrolet', 'Malibu',    'Sedan', 5, 5, 5],
        # Cruze: discontinued, was below average especially with diesel variant
        ['Chevrolet', 'Cruze',     'Sedan', 4, 4, 4],
    ],

    # ── HYUNDAI ───────────────────────────────────────────────────────────────
    # CR 2026: #8 brand (score 48). JD Power improving year over year.
    # Theta II engine recall hurt scores but mostly affects older models.
    # Newer models (Ioniq, Palisade) are significantly better.
    'Hyundai': [
        # Ioniq: purpose-built hybrid/EV platform, excellent reliability
        ['Hyundai', 'Ioniq',    'Sedan', 9, 8, 8],
        # Palisade: above average 3-row, strong drivetrain
        ['Hyundai', 'Palisade', 'SUV',   7, 7, 7],
        # Tucson: improving, newer gen more reliable than old
        ['Hyundai', 'Tucson',   'SUV',   7, 7, 6],
        # Sonata: Theta II recall affected older models, newer gen better
        ['Hyundai', 'Sonata',   'Sedan', 7, 7, 6],
        # Elantra: smaller, simpler, avoids the bigger engine issues
        ['Hyundai', 'Elantra',  'Sedan', 7, 7, 7],
    ],
}


for brand, models in full_market_data.items():
    add_brand_to_reliability(brand, models)

print("brand_model_reliability.csv updated successfully.")
