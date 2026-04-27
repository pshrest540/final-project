from fastapi import APIRouter, HTTPException
from api.db.session import test_db_connection

router = APIRouter(prefix="/db", tags=["Database"])

@router.get("/health")
def db_health():
    try:
        if not test_db_connection():
            raise HTTPException(status_code=500, detail="Database connection failed")
        return {"status": "ok", "message": "Database connection successful"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
