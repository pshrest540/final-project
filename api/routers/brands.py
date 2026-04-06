import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.schemas import BrandsResponse, BrandEntry, ModelEntry

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("", response_model=BrandsResponse)
def get_brands():
    """
    Returns all available brands and their models with reliability scores.
    Used to populate dropdowns in the frontend.
    """
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
        df       = pd.read_csv(os.path.join(DATA_DIR, "brand_model_reliability.csv"))

        brands = []
        for brand_name, group in df.groupby("brand"):
            models = [
                ModelEntry(
                    model=row["model"],
                    type=row["type"],
                    elec_score=int(row["elec_score"]),
                    drive_score=int(row["drive_score"]),
                    engine_score=int(row["engine_score"]),
                )
                for _, row in group.iterrows()
            ]
            brands.append(BrandEntry(brand=brand_name, models=models))

        return BrandsResponse(brands=sorted(brands, key=lambda b: b.brand))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
