import sqlite3
from typing import Optional, Dict, Any, List
import difflib
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[2] / "rferral_agent_data.sqlite3"


def get_conn():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            name TEXT,
            dob TEXT,
            raw JSON
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER,
            item_code TEXT,
            hipc_code TEXT,
            price TEXT,
            description TEXT,
            raw JSON,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
        """
    )
    conn.commit()
    conn.close()


def save_patient(patient: Dict[str, Any]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (name, dob, raw) VALUES (?, ?, ?)",
        (patient.get("name"), patient.get("dob"), str(patient)),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def save_order(order: Dict[str, Any], patient_id: Optional[int] = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (patient_id, item_code, hipc_code, price, description, raw) VALUES (?, ?, ?, ?, ?, ?)",
        (
            patient_id,
            order.get("item_code"),
            order.get("hipc_code"),
            order.get("price"),
            order.get("description"),
            str(order),
        ),
    )
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return oid


def list_patient_names() -> List[str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM patients WHERE name IS NOT NULL")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def find_patient_by_name(name: str, cutoff: float = 0.6) -> Optional[Dict[str, Any]]:
    """Fuzzy-match a patient name against existing patients. Returns row dict if found."""
    if not name:
        return None
    names = list_patient_names()
    matches = difflib.get_close_matches(name, names, n=1, cutoff=cutoff)
    if not matches:
        return None
    # fetch full row
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE name = ?", (matches[0],))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
