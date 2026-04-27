

BRAND_MODELS = {
    "Toyota": [
        "Camry",
        "Corolla",
        "RAV4",
        "Tacoma",
        "4Runner",
    ],
    "Honda": [
        "Civic",
        "Accord",
        "CR-V",
        "Pilot",
        "Ridgeline",
    ],
    "Subaru": [
        "Forester",
        "Outback",
        "Crosstrek",
        "Impreza",
        "WRX",
        "Ascent",
    ],
    "Nissan": [
        "Altima",
        "Sentra",
        "Rogue",
        "Pathfinder",
        "Frontier",
    ],
    "BMW": [
        "3 Series",
        "5 Series",
        "X3",
        "X5",
        "7 Series",
    ],
    "Ford": [
        "F-150",
        "Mustang",
        "Explorer",
        "Focus",
        "EcoSport",
    ],
    "Chevrolet": [
        "Silverado",
        "Tahoe",
        "Trax",
        "Malibu",
        "Cruze",
    ],
    "Hyundai": [
        "Ioniq",
        "Palisade",
        "Tucson",
        "Sonata",
        "Elantra",
    ],
}

START_YEAR = 2000
END_YEAR = 2025


def generate_vehicle_list():
    vehicles = []
    for brand, models in BRAND_MODELS.items():
        for model in models:
            for year in range(START_YEAR, END_YEAR + 1):
                vehicles.append((brand, model, year))
    return vehicles