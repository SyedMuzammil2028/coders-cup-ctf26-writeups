"""Explicit local preview; uses the same encoder without writing data into assets."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from generate import encode_flag


def main():
    try:
        payload = json.dumps({'ciphertext': encode_flag(os.environ.get('FLAG'))}).encode()
    except (ValueError, UnicodeError):
        raise SystemExit('Preview failed: provide an explicit valid dummy FLAG.')

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split('?')[0] == '/ciphertext.json':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                super().do_GET()

    handler = partial(Handler, directory=str(Path(__file__).parent / 'website'))
    server = ThreadingHTTPServer(('127.0.0.1', 8080), handler)
    print('Local preview: http://127.0.0.1:8080', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
