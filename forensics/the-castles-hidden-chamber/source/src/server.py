#!/usr/bin/env python3
"""Minimal bounded HTTP service for the generated JPEG artifact."""

from __future__ import annotations

import argparse
import os
import signal
import socket
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit


MAX_CONCURRENT_DOWNLOADS = 8
SEND_CHUNK_BYTES = 1024 * 1024


class ArtifactHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "CastleArchive/1.0"
    sys_version = ""

    def log_message(self, _format: str, *_arguments: object) -> None:
        return

    def _plain_error(self, status: int, message: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(message)))
        self.send_header("Cache-Control", "private, no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(message)

    def _serve_index(self, include_body: bool) -> None:
        index: Path = self.server.index_path  # type: ignore[attr-defined]
        try:
            page = index.read_bytes()
        except OSError:
            self._plain_error(503, b"Landing page unavailable\n")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "private, no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; "
            "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        if include_body:
            self.wfile.write(page)

    def _serve_artifact(self, include_body: bool, *, attachment: bool) -> None:
        artifact: Path = self.server.artifact_path  # type: ignore[attr-defined]
        try:
            size = artifact.stat().st_size
        except OSError:
            self._plain_error(503, b"Artifact unavailable\n")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        disposition = "attachment" if attachment else "inline"
        self.send_header("Content-Disposition", f'{disposition}; filename="challenge.jpg"')
        self.send_header("Content-Length", str(size))
        self.send_header("Cache-Control", "private, no-store, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not include_body:
            return
        try:
            with artifact.open("rb", buffering=0) as handle:
                offset = 0
                output_fd = self.connection.fileno()
                while offset < size:
                    sent = os.sendfile(output_fd, handle.fileno(), offset, min(SEND_CHUNK_BYTES, size - offset))
                    if sent == 0:
                        raise OSError("sendfile returned zero bytes")
                    offset += sent
        except (BrokenPipeError, ConnectionResetError, OSError):
            return

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/":
            self._serve_index(include_body=True)
        elif path == "/challenge.jpg":
            self._serve_artifact(include_body=True, attachment=True)
        elif path == "/preview.jpg":
            self._serve_artifact(include_body=True, attachment=False)
        else:
            self._plain_error(404, b"Not found\n")

    def do_HEAD(self) -> None:
        path = urlsplit(self.path).path
        if path == "/":
            self._serve_index(include_body=False)
        elif path == "/challenge.jpg":
            self._serve_artifact(include_body=False, attachment=True)
        elif path == "/preview.jpg":
            self._serve_artifact(include_body=False, attachment=False)
        else:
            self._plain_error(404, b"Not found\n")

    def do_POST(self) -> None:
        self._plain_error(405, b"Method not allowed\n")


class BoundedThreadingMixIn(socketserver.ThreadingMixIn):
    daemon_threads = True
    block_on_close = True

    def __init__(self, *arguments: object, **keywords: object) -> None:
        self._download_slots = threading.BoundedSemaphore(MAX_CONCURRENT_DOWNLOADS)
        super().__init__(*arguments, **keywords)

    def process_request(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        if not self._download_slots.acquire(blocking=False):
            try:
                request.sendall(
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: 11\r\n"
                    b"Connection: close\r\n\r\nTry later.\n"
                )
            finally:
                request.close()
            return
        super().process_request(request, client_address)

    def process_request_thread(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._download_slots.release()


class ArtifactServer(BoundedThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], artifact: Path, index: Path):
        self.artifact_path = artifact
        self.index_path = index
        super().__init__(address, ArtifactHandler)


def valid_port(raw: str) -> int:
    try:
        port = int(raw)
    except ValueError as error:
        raise ValueError("PORT must be an integer") from error
    if not 1 <= port <= 65_535:
        raise ValueError("PORT must be between 1 and 65535")
    return port


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    arguments = parser.parse_args()
    artifact = arguments.artifact.resolve()
    index = arguments.index.resolve()
    if not artifact.is_file() or artifact.stat().st_size == 0:
        parser.error("artifact is missing or empty")
    if not index.is_file() or index.stat().st_size == 0:
        parser.error("landing page is missing or empty")
    port = valid_port(os.environ.get("PORT", "8000"))
    with ArtifactServer(("0.0.0.0", port), artifact, index) as server:
        def stop(_signum: int, _frame: object) -> None:
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        print(f"serving challenge.jpg on port {port}", flush=True)
        server.serve_forever(poll_interval=0.25)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

