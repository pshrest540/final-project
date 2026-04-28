from pathlib import Path

from sqlalchemy import text

from api.db.session import engine


ROOT_DIR = Path(__file__).resolve().parents[2]
MIGRATION_PATH = ROOT_DIR / "supabase" / "migrations" / "20260428_app_update.sql"


REQUIRED_PREDICTION_COLUMNS = [
    "cv_wellness",
    "wb_wellness",
    "brk_wellness",
    "bat_wellness",
    "alt_wellness",
    "sta_wellness",
    "coolant_wellness",
    "ignition_wellness",
    "fuel_wellness",
]


def run_migration() -> None:
    sql = MIGRATION_PATH.read_text(encoding="utf-8")
    raw_connection = engine.raw_connection()
    try:
        with raw_connection.cursor() as cursor:
            cursor.execute(sql)
        raw_connection.commit()
    except Exception:
        raw_connection.rollback()
        raise
    finally:
        raw_connection.close()


def verify_schema() -> list[str]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                select column_name
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'wellness_predictions'
                  and column_name in (
                      'cv_wellness',
                      'wb_wellness',
                      'brk_wellness',
                      'bat_wellness',
                      'alt_wellness',
                      'sta_wellness',
                      'coolant_wellness',
                      'ignition_wellness',
                      'fuel_wellness'
                  )
                """
            )
        ).scalars()
        existing = set(rows)
    return [column for column in REQUIRED_PREDICTION_COLUMNS if column not in existing]


if __name__ == "__main__":
    print(f"Running migration: {MIGRATION_PATH}")
    run_migration()
    missing = verify_schema()
    if missing:
        raise SystemExit(f"Migration finished, but columns are still missing: {missing}")
    print("Migration complete. wellness_predictions has all component score columns.")
