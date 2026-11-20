"""Deliberately narrow HTTP surface for the downloadable bytecode artifact."""

import argparse
import os
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def make_handler(artifact_path, index_path):
    """Create a handler that serves exactly / and /download, never directories."""
    artifact = Path(artifact_path)
    index = Path(index_path)

    class ChallengeHandler(BaseHTTPRequestHandler):
        server_version = "ForbiddenArchive/1.0"
        protocol_version = "HTTP/1.1"

        def log_message(self, format_string, *arguments):
            # Avoid standard request logging: it adds no operational value and
            # keeps the service's output minimal.
            return

        def _send_file_headers(self, target, content_type, attachment=None):
            size = target.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            if attachment:
                self.send_header("Content-Disposition", 'attachment; filename="{}"'.format(attachment))
            self.end_headers()

        def _route(self, send_body):
            path = urlsplit(self.path).path
            if path == "/":
                target, content_type, attachment = index, "text/html; charset=utf-8", None
            elif path == "/download":
                target, content_type, attachment = artifact, "application/octet-stream", "malware.pyc"
            else:
                self.send_error(404, "Not found")
                return
            try:
                self._send_file_headers(target, content_type, attachment)
                if send_body:
                    with target.open("rb") as handle:
                        shutil.copyfileobj(handle, self.wfile, length=64 * 1024)
            except (FileNotFoundError, OSError):
                if not self.wfile.closed:
                    self.send_error(503, "Artifact unavailable")

        def do_GET(self):
            self._route(send_body=True)

        def do_HEAD(self):
            self._route(send_body=False)

        def do_POST(self):
            self.send_error(405, "Method not allowed")

    return ChallengeHandler


def valid_port(value):
    try:
        port = int(value)
    except ValueError:
        raise ValueError("PORT must be an integer")
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    return port


def main(argv=None):
    parser = argparse.ArgumentParser(description="Serve the one challenge artifact")
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--public-dir", type=Path, required=True)
    arguments = parser.parse_args(argv)
    artifact = arguments.artifact.resolve()
    index = (arguments.public_dir / "index.html").resolve()
    if not artifact.is_file() or artifact.stat().st_size == 0:
        parser.error("artifact is missing or empty")
    if not index.is_file():
        parser.error("public index is missing")
    try:
        port = valid_port(os.environ.get("PORT", "8080"))
    except ValueError as error:
        parser.error(str(error))
    HTTPServer(("0.0.0.0", port), make_handler(artifact, index)).serve_forever()


if __name__ == "__main__":
    main()
