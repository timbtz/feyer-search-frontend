"""Local read-only frontend server. Requires Python 3.9+ and no packages."""
import argparse
import json
import time
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
ASSETS = {'index.html', 'app.js', 'style.css', 'pds-loader.js', 'pds-variables.css',
          'pds-normalize.css', 'pds-font-face.css', 'search-architecture.svg'}
LIMIT = 32 * 1024 * 1024
CSP = ("default-src 'self'; connect-src 'self' https://cdn.ui.porsche.com; "
       "script-src 'self' https://cdn.ui.porsche.com; style-src 'self' 'unsafe-inline'; "
       "font-src 'self' https://cdn.ui.porsche.com; img-src 'self' data: https://cdn.ui.porsche.com; "
       "object-src 'none'; frame-ancestors 'none'")


def state_body(api_url=None, snapshot=None, team_snapshot=None):
    if team_snapshot:
        path = Path(team_snapshot)
        with path.open('rb') as stream:
            raw = stream.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('Team snapshot exceeds the size limit')
        ledger = json.loads(raw)
        if not isinstance(ledger, dict) or ledger.get('schema') != 'feyer-team-search-v1' or not isinstance(ledger.get('tasks'), dict) or not isinstance(ledger.get('observations'), dict):
            raise ValueError('Unsupported team snapshot')
        observed = path.stat().st_mtime
        return json.dumps({'campaigns': [], 'snapshot': True, 'generated_at': observed, 'team_search': ledger, 'team_search_source': {'available': True, 'mode': 'local_snapshot', 'observed_at': observed, 'stale': time.time()-observed > 90, 'source': 'Local team ledger export', 'error': None}}, allow_nan=False).encode()
    if api_url:
        with urlopen(api_url.rstrip('/') + '/api/state', timeout=10) as response:
            body = response.read(LIMIT + 1)
    else:
        path = Path(snapshot) if snapshot else ROOT / 'fixtures' / 'demo-state.json'
        with path.open('rb') as stream:
            body = stream.read(LIMIT + 1)
    if len(body) > LIMIT:
        raise ValueError('Snapshot exceeds the size limit')
    state = json.loads(body)
    if not isinstance(state, dict) or not isinstance(state.get('campaigns'), list):
        raise ValueError('Snapshot must include a campaigns array')
    if not api_url and not snapshot:
        state['demo'] = True
    elif snapshot:
        state['snapshot'] = True
    return json.dumps(state, allow_nan=False).encode()


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, api_url=None, snapshot=None, team_snapshot=None, **kwargs):
        self.api_url, self.snapshot, self.team_snapshot = api_url, snapshot, team_snapshot
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.headers.get('Host') not in (f'localhost:{self.server.server_port}', f'127.0.0.1:{self.server.server_port}'):
            self.send_error(403, 'Loopback host required')
            return
        path = urlsplit(self.path).path
        if path == '/api/state':
            try:
                body = state_body(self.api_url, self.snapshot, self.team_snapshot)
            except (OSError, ValueError, HTTPError, URLError):
                self.send_error(503, 'Search evidence unavailable')
                return
            mime = 'application/json'
        else:
            name = 'index.html' if path == '/' else path[1:]
            if name not in ASSETS:
                self.send_error(404)
                return
            body = (ROOT / name).read_bytes()
            mime = {'html': 'text/html', 'js': 'text/javascript', 'css': 'text/css', 'svg': 'image/svg+xml'}[name.rsplit('.', 1)[1]]
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', CSP)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--demo', action='store_true', help='Use explicitly synthetic sample evidence')
    modes.add_argument('--api-url', help='Origin of an existing read-only observatory, e.g. http://127.0.0.1:8765')
    modes.add_argument('--snapshot', type=Path, help='Local sanitized /api/state JSON export (keep out of Git)')
    modes.add_argument('--team-snapshot', type=Path, help='Local sanitized feyer-team-search-v1 ledger export')
    parser.add_argument('--port', type=int, default=8770)
    args = parser.parse_args()
    if args.api_url:
        url = urlsplit(args.api_url)
        if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
            parser.error('--api-url must be an HTTP(S) origin without credentials or a path')
    handler = partial(Handler, api_url=args.api_url, snapshot=args.snapshot, team_snapshot=args.team_snapshot)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    server.daemon_threads = True
    mode = 'synthetic demo' if args.demo else 'local snapshot' if args.snapshot or args.team_snapshot else 'read-only API'
    print(f'Feyer search frontend: http://localhost:{server.server_port} ({mode})', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
