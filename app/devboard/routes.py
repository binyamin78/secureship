"""HTTP layer: HTML pages and JSON API."""
import hashlib
import os
import socket

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from .metrics import WORK
from .store import store

VERSION = os.environ.get("APP_VERSION", "dev")

web = Blueprint("web", __name__)
api = Blueprint("api", __name__)


@web.get("/")
def index():
    return render_template(
        "index.html", notes=store.list(), version=VERSION, pod=socket.gethostname()
    )


@web.post("/notes")
def add_note():
    author = request.form.get("author", "").strip()[:40] or "anonymous"
    text = request.form.get("text", "").strip()[:280]
    if text:
        store.add(author, text)
    return redirect(url_for("web.index"))


@api.get("/notes")
def list_notes():
    return jsonify([n.to_dict() for n in store.list()])


@api.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()[:280]
    if not text:
        return jsonify(error="text is required"), 400
    note = store.add(str(data.get("author", "anonymous"))[:40], text)
    return jsonify(note.to_dict()), 201


@api.get("/work")
def work():
    """CPU-heavy endpoint used by the load test to trigger the HPA."""
    rounds = min(int(request.args.get("rounds", 20000)), 200000)
    digest = b"secureship"
    for _ in range(rounds):
        digest = hashlib.sha256(digest).digest()
    WORK.inc()
    return jsonify(rounds=rounds, digest=digest.hex()[:16], pod=socket.gethostname())


@api.get("/health")
def health():
    return jsonify(status="ok", version=VERSION, pod=socket.gethostname())
