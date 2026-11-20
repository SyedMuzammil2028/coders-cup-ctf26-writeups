"""HTTP service for The Last Newline. Uses the Python standard library only."""

from email import policy
from email.errors import MessageError
from email.parser import BytesHeaderParser
from hashlib import sha256
from hmac import compare_digest
from http.client import HTTPException
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import signal
from socketserver import ThreadingMixIn
import sys
from threading import BoundedSemaphore
from urllib.parse import parse_qs, urlsplit

from generate import CURRENT, generate_evidence


MAX_FILE = 16 * 1024
MAX_REQUEST = 24 * 1024
MAX_FIELD = 128
MAX_HEADERS = 12 * 1024
DENIED = "Vault access denied. The submitted recovery evidence could not be verified."
UNLOCKED = "Integrity restored. Keeper's Vault unlocked."
STATIC = {
    "/static/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/static/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
HTML = "text/html; charset=utf-8"
PLAIN = "text/plain; charset=utf-8"
CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; "
       "connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
PART_NAMES = {"document", "phrase", "missing_byte"}
BOUNDARY = re.compile(rb"[0-9A-Za-z'()+_,./:=? -]{1,70}")
REVISION_API = re.compile(r"/api/revisions/([0-9]{2})(?:/(preview|download))?")


class InvalidUpload(ValueError):
    """An upload violated the form's structure or size limits."""

    def __init__(self, status=400):
        self.status = status


class HeaderBudget:
    """Limit the total header bytes before the standard HTTP parser allocates them."""

    def __init__(self, stream):
        self.stream = stream
        self.remaining = MAX_HEADERS

    def readline(self, size):
        line = self.stream.readline(min(size, self.remaining + 1))
        self.remaining -= len(line)
        if self.remaining < 0:
            raise HTTPException("Request headers too large")
        return line


def read_parts(body, boundary):
    """Read browser multipart framing while leaving the part payloads as bytes."""
    marker = b"--" + boundary
    if not body.startswith(marker + b"\r\n"):
        raise InvalidUpload()

    delimiter = re.compile(rb"\r\n" + re.escape(marker) + rb"(\r\n|--(?:\r\n)?\Z)")
    start = len(marker) + 2
    parts = {}
    for match in delimiter.finditer(body, start):
        headers, separator, payload = body[start:match.start()].partition(b"\r\n\r\n")
        if not separator or len(headers) > 2048 or b"\x00" in headers:
            raise InvalidUpload()
        metadata = BytesHeaderParser(policy=policy.HTTP).parsebytes(headers + b"\r\n\r\n")
        dispositions = metadata.get_all("Content-Disposition", [])
        if metadata.defects or len(dispositions) != 1:
            raise InvalidUpload()
        # No transfer encoding is accepted.
        if {key.lower() for key in metadata.keys()} - {"content-disposition", "content-type"}:
            raise InvalidUpload()
        if len(metadata.get_all("Content-Type", [])) > 1:
            raise InvalidUpload()
        disposition = dispositions[0]
        name = disposition.params.get("name")
        if (disposition.defects or disposition.content_disposition != "form-data"
                or name not in PART_NAMES or name in parts
                or ("filename" in disposition.params) != (name == "document")):
            raise InvalidUpload()
        limit = MAX_FILE if name == "document" else MAX_FIELD
        if len(payload) > limit:
            raise InvalidUpload(413)
        parts[name] = payload
        if match[1].startswith(b"--"):
            if parts.keys() != PART_NAMES or not parts["document"]:
                raise InvalidUpload()
            return parts
        start = match.end()
    raise InvalidUpload()


class ArchiveHandler(BaseHTTPRequestHandler):
    server_version = "KeeperArchive"
    sys_version = ""

    def parse_request(self):
        stream = self.rfile
        self.rfile = HeaderBudget(stream)
        try:
            return super().parse_request()
        finally:
            self.rfile = stream

    def log_message(self, format, *args):
        # Request targets and player input are deliberately omitted from logs.
        pass

    def send_error(self, code, message=None, explain=None):
        self.reply_json(code, {"message": "The archive could not process this request."})

    def reply(self, status, content_type, body, *, filename=None):
        self.close_connection = True
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Referrer-Policy", "no-referrer")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def reply_json(self, status, value):
        self.reply(status, "application/json; charset=utf-8", json.dumps(value).encode("utf-8"))

    def request_target(self):
        try:
            target = urlsplit(self.path)
        except ValueError:
            return None
        if target.scheme or target.netloc or target.fragment or not target.path.startswith("/"):
            return None
        return target

    def do_GET(self):
        target = self.request_target()
        if target is None:
            return self.send_error(400)
        path = target.path
        evidence = self.server.evidence
        if path in self.server.pages:
            return self.reply(200, HTML, self.server.index)
        if path in self.server.assets:
            content_type, body = self.server.assets[path]
            return self.reply(200, content_type, body)
        if path == "/healthz":
            return self.reply(200, PLAIN, b"ok\n")
        if path == "/api/archive":
            return self.reply_json(200, {
                "case_reference": evidence.case_reference,
                **evidence.revisions[CURRENT].listing(),
            })
        if path == "/api/revisions":
            return self.reply_json(200, {
                "case_reference": evidence.case_reference,
                "revisions": [revision.summary() for revision in evidence.revisions.values()],
            })

        route = REVISION_API.fullmatch(path)
        if route and route[1] in evidence.revisions:
            revision = evidence.revisions[route[1]]
            if route[2] is None:
                return self.reply_json(200, revision.listing())
            return self.serve_evidence(revision, route[2], target.query)
        return self.send_error(404)

    do_HEAD = do_GET

    def serve_evidence(self, revision, action, query):
        try:
            values = parse_qs(query, strict_parsing=True, max_num_fields=1)
        except ValueError:
            return self.send_error(400)
        names = values.get("file", [])
        if len(names) != 1 or names[0] not in revision.files:
            return self.send_error(404)
        name = names[0]
        if action == "download":
            return self.reply(200, "application/octet-stream", revision.files[name],
                              filename=name.rsplit("/", 1)[-1])
        return self.reply(200, PLAIN, revision.files[name])

    def receive_upload(self):
        lengths = self.headers.get_all("Content-Length", [])
        content_types = self.headers.get_all("Content-Type", [])
        if self.headers.get_all("Transfer-Encoding") or len(lengths) != 1:
            raise InvalidUpload()
        if not re.fullmatch(r"[0-9]{1,10}", lengths[0]):
            raise InvalidUpload()
        length = int(lengths[0])
        if length > MAX_REQUEST:
            raise InvalidUpload(413)
        if (len(content_types) != 1 or len(content_types[0]) > 256
                or self.headers.get_content_type() != "multipart/form-data"):
            raise InvalidUpload(415)
        content_type = policy.HTTP.header_factory("Content-Type", content_types[0])
        try:
            boundary = content_type.params.get("boundary", "").encode("ascii")
        except UnicodeEncodeError as exc:
            raise InvalidUpload() from exc
        if content_type.defects or not BOUNDARY.fullmatch(boundary) or boundary.endswith(b" "):
            raise InvalidUpload()
        try:
            body = self.rfile.read(length)
        except TimeoutError as exc:
            raise InvalidUpload(408) from exc
        if len(body) != length:
            raise InvalidUpload()
        return read_parts(body, boundary)

    def do_POST(self):
        target = self.request_target()
        if target is None:
            return self.send_error(400)
        if target.path != "/api/vault/verify":
            return self.send_error(404)
        try:
            parts = self.receive_upload()
        except InvalidUpload as exc:
            return self.reply_json(exc.status, {"message": DENIED})
        except (MessageError, RecursionError):
            # The email parser may reject malformed or deeply nested part metadata.
            return self.reply_json(400, {"message": DENIED})

        evidence = self.server.evidence
        document_ok = compare_digest(sha256(parts["document"]).digest(), evidence.certified_digest)
        phrase_ok = compare_digest(parts["phrase"].strip(), evidence.recovery_phrase)
        byte_ok = compare_digest(parts["missing_byte"].strip().upper(), b"0A")
        if document_ok and phrase_ok and byte_ok:
            return self.reply_json(200, {"message": UNLOCKED, "flag": self.server.flag})
        return self.reply_json(403, {"message": DENIED})


class ArchiveServer(ThreadingMixIn, HTTPServer):
    """Bound concurrent sockets per instance and let in-flight requests finish on stop."""

    request_queue_size = 16

    def __init__(self, address, flag):
        self.flag = flag
        self.evidence = generate_evidence()
        self.slots = BoundedSemaphore(8)
        directory = Path(__file__).resolve().parent / "static"
        self.index = (directory / "index.html").read_bytes()
        self.assets = {url: (content_type, (directory / name).read_bytes())
                       for url, (name, content_type) in STATIC.items()}
        self.pages = {"/", "/revisions", "/vault"}
        self.pages.update(f"/revisions/{number}" for number in self.evidence.revisions)
        super().__init__(address, ArchiveHandler)

    def process_request(self, request, client_address):
        request.settimeout(5)
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def handle_error(self, request, client_address):
        # Never print exceptions or player data to the container logs.
        pass


def main():
    try:
        flag = os.environ["FLAG"]
    except KeyError:
        flag = ""
    if not flag.strip():
        print("Startup refused: set the FLAG environment variable.", file=sys.stderr)
        return 1

    # A flag may contain surrounding whitespace. Only the startup check strips it.
    with ArchiveServer(("0.0.0.0", 8000), flag) as server:
        print("Keeper's Archive listening on port 8000.", flush=True)
        # The default SIGINT handler raises KeyboardInterrupt on the main thread.
        # Use the same path for Docker's SIGTERM to exit the serving loop cleanly.
        signal.signal(signal.SIGTERM, signal.default_int_handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
