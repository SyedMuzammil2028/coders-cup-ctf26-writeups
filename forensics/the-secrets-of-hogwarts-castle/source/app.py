"""Hogwarts Castle Archives public application.

The challenge images are immutable, pre-generated static assets.  Nothing in
this application writes, re-encodes, or dynamically creates challenge files.
"""

from __future__ import annotations

import os

from flask import Flask, render_template


app = Flask(__name__)
app.config.update(
    SEND_FILE_MAX_AGE_DEFAULT=60 * 60 * 24 * 30,
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/gallery")
def gallery():
    return render_template("gallery.html")


@app.get("/health")
def health():
    return {"status": "ok", "service": "hogwarts-castle-archives"}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, debug=False)
