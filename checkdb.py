"""Run with: python checkdb.py"""

from api.db.session import test_db_connection

if test_db_connection():
    print("OK — database connection successful.")
else:
    print("FAILED — could not connect to database.")
