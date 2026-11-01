from flask import Flask, request, jsonify, session
from .agent import answer
from .rag import ingest

app = Flask(__name__)
app.secret_key = "dev"


@app.post("/chat")
def chat():
    data = request.get_json()
    return jsonify(reply=answer(data["message"], data.get("page_url")))


@app.post("/upload")
def upload():
    data = request.get_json()
    ingest(data["id"], data["text"], session["tenant_id"])
    return jsonify(ok=True)
