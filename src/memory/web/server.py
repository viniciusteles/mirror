"""Local read-only web server for the Mirror web console."""

from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from memory.web.docs import DocsBrowser

STATIC_DIR = Path(__file__).parent / "static"


class MirrorWebHandler(BaseHTTPRequestHandler):
    browser: DocsBrowser

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/docs/tree":
            self._send_json([node.to_dict() for node in self.browser.tree()])
            return

        if parsed.path == "/api/docs/file":
            query = parse_qs(parsed.query)
            doc_path = query.get("path", [""])[0]
            try:
                self._send_json(
                    {
                        "path": doc_path,
                        "markdown": self.browser.read_markdown(doc_path),
                        "html": self.browser.render_html(doc_path),
                    }
                )
            except (FileNotFoundError, ValueError) as exc:
                self._send_json({"error": str(exc)}, status=404)
            return

        self._send_static(parsed.path)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self, request_path: str) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        candidate = (STATIC_DIR / relative).resolve()
        if not candidate.is_file() or not candidate.is_relative_to(STATIC_DIR.resolve()):
            self.send_error(404)
            return

        body = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(host: str = "127.0.0.1", port: int = 8765, root: Path | None = None) -> None:
    browser = DocsBrowser(root=root)

    class Handler(MirrorWebHandler):
        pass

    Handler.browser = browser
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Mirror Web Console running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the local Mirror Web Console")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)
    serve(host=args.host, port=args.port, root=args.root)


if __name__ == "__main__":
    main()
