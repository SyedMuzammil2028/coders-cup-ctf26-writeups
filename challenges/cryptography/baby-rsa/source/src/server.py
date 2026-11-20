#!/usr/bin/env python3
"""Bounded-concurrency TCP service for the Baby RSA CTF challenge."""

from __future__ import annotations

import os
import signal
import socket
import socketserver
import sys
import threading

from rsa_generator import generate_challenge, render_challenge


DEFAULT_PORT = 1337
MAX_CONNECTIONS = 4
CLIENT_TIMEOUT_SECONDS = 15


def load_flag() -> str:
    try:
        FLAG = os.environ["FLAG"]
    except KeyError as error:
        raise RuntimeError("required runtime flag is not configured") from error
    if not FLAG or not FLAG.startswith("ACM{") or not FLAG.endswith("}"):
        raise RuntimeError("required runtime flag is invalid")
    if len(FLAG) > 256 or not FLAG.isascii():
        raise RuntimeError("required runtime flag is invalid")
    return FLAG


def load_port() -> int:
    raw = os.environ.get("PORT", str(DEFAULT_PORT))
    try:
        port = int(raw)
    except ValueError as error:
        raise RuntimeError("configured port is invalid") from error
    if not 1 <= port <= 65_535:
        raise RuntimeError("configured port is invalid")
    return port


class BoundedThreadingMixIn(socketserver.ThreadingMixIn):
    daemon_threads = True
    block_on_close = True
    _slots = threading.BoundedSemaphore(MAX_CONNECTIONS)

    def process_request(self, request, client_address):
        if not self._slots.acquire(blocking=False):
            try:
                request.sendall(b"Server busy. Please reconnect shortly.\n")
            except OSError:
                pass
            finally:
                request.close()
            return
        super().process_request(request, client_address)

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()


class BabyRSARequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        self.request.settimeout(CLIENT_TIMEOUT_SECONDS)
        try:
            challenge = generate_challenge(self.server.flag)
            self.request.sendall(render_challenge(challenge))
        except (BrokenPipeError, ConnectionResetError, socket.timeout, OSError):
            return


class BabyRSAServer(BoundedThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], flag: str):
        self.flag = flag
        super().__init__(address, BabyRSARequestHandler)


def main() -> int:
    try:
        flag = load_flag()
        port = load_port()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 64

    with BabyRSAServer(("0.0.0.0", port), flag) as server:
        def stop(_signal, _frame):
            threading.Thread(target=server.shutdown, daemon=True).start()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        try:
            server.serve_forever(poll_interval=0.25)
        finally:
            server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
