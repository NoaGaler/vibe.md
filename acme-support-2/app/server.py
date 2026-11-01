import os
from flask import Flask, request, jsonify, session, abort
from .agent import answer
from .rag import ingest

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


def current_user():
    if "user_id" not in session:
        abort(401)
    return session["user_id"], session["tenant_id"]


@app.post("/chat")
def chat():
    user_id, tenant_id = current_user()
    return jsonify(reply=answer(user_id, tenant_id, request.get_json()["message"]))


@app.post("/upload")
def upload():
    _, tenant_id = current_user()
    data = request.get_json()
    ingest(data["id"], data["text"], tenant_id)
    return jsonify(ok=True)
