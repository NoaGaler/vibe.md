import sqlite3
from pathlib import Path

DB = sqlite3.connect("acme.db", check_same_thread=False)
DOCS_DIR = Path("customer_files").resolve()


class ToolError(Exception):
    pass


def get_order(user_id: str, order_id: str):
    """Look up one order that belongs to the signed-in user."""
    row = DB.execute(
        "SELECT id, status, total FROM orders WHERE id = ? AND user_id = ?",
        (order_id, user_id),
    ).fetchone()
    if row is None:
        raise ToolError("order not found")
    return {"id": row[0], "status": row[1], "total": row[2]}


def read_customer_file(user_id: str, name: str):
    """Read one of the signed-in user's own uploaded files."""
    base = (DOCS_DIR / user_id).resolve()
    path = (base / name).resolve()
    if not path.is_relative_to(base):
        raise ToolError("file not allowed")
    return path.read_text()


# user_id is never chosen by the model: the agent binds it from the session.
TOOLS = {"get_order": get_order, "read_customer_file": read_customer_file}
