import os
from rferral_agent.server.app import db


def test_db_init_and_save(tmp_path):
    # Use a temporary DB file by overriding DB_FILE path
    db.DB_FILE = tmp_path / "test_db.sqlite3"
    db.init_db()

    pid = db.save_patient({"name": "Alice Smith", "dob": "01/01/1980"})
    assert isinstance(pid, int) and pid > 0

    oid = db.save_order({"item_code": "X-1", "description": "Test item"}, patient_id=pid)
    assert isinstance(oid, int) and oid > 0

    match = db.find_patient_by_name("Alice Smith")
    assert match and match.get("name") == "Alice Smith"
