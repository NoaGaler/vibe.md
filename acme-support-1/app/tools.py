import sqlite3
import smtplib
from email.message import EmailMessage

DB = sqlite3.connect("acme.db", check_same_thread=False)


def run_sql(query: str):
    """Run a SQL query against the Acme database."""
    return DB.execute(query).fetchall()


def read_file(path: str):
    """Read a file from the server."""
    with open(path) as f:
        return f.read()


def send_email(to: str, subject: str, body: str):
    """Send an email on behalf of Acme support."""
    msg = EmailMessage()
    msg["To"], msg["Subject"], msg["From"] = to, subject, "support@acme.example"
    msg.set_content(body)
    with smtplib.SMTP("localhost") as s:
        s.send_message(msg)
    return "sent"


TOOLS = {"run_sql": run_sql, "read_file": read_file, "send_email": send_email}
