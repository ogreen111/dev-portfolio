#!/usr/bin/env python3
"""Read-only doc server for the portfolio index (index.html).

Serves ~/Documents/dev so the portfolio site is reachable on the LAN. It
terminates its own TLS (PORTFOLIO_SSL_CERTFILE/KEYFILE, mkcert cert) — no
reverse proxy. The dev tree is full of things that must not leave the box
(.env files, SQLite databases, .git internals), so this serves an allowlist
of doc/image file types only and refuses any path with a dot-prefixed
component.

Run: PORTFOLIO_PORT=18737 python3 portfolio_server.py
"""

import html
import io
import os
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTS = {
    ".html", ".md", ".docx", ".pdf", ".txt",
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
}


class DocHandler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        # text/plain so browsers display markdown instead of downloading it
        ".md": "text/plain; charset=utf-8",
    }

    def send_head(self):
        url_path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        parts = [p for p in url_path.split("/") if p]
        if any(p.startswith(".") for p in parts):
            self.send_error(404)
            return None
        if not os.path.isdir(self.translate_path(self.path)):
            if os.path.splitext(url_path)[1].lower() not in ALLOWED_EXTS:
                self.send_error(404, "File type not served")
                return None
        return super().send_head()

    def list_directory(self, path):
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except OSError:
            self.send_error(404)
            return None
        rel = html.escape(urllib.parse.unquote(urllib.parse.urlsplit(self.path).path))
        lines = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            f"<title>{rel}</title></head><body>",
            f"<h1>{rel}</h1><ul>",
            "<li><a href='../'>../</a></li>",
        ]
        for e in entries:
            if e.name.startswith("."):
                continue
            if not e.is_dir() and os.path.splitext(e.name)[1].lower() not in ALLOWED_EXTS:
                continue
            href = urllib.parse.quote(e.name) + ("/" if e.is_dir() else "")
            lines.append(f"<li><a href='{href}'>{html.escape(e.name)}{'/' if e.is_dir() else ''}</a></li>")
        lines.append("</ul></body></html>")
        encoded = "\n".join(lines).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return io.BytesIO(encoded)


def main():
    host = os.environ.get("PORTFOLIO_HOST", "127.0.0.1")
    port = int(os.environ.get("PORTFOLIO_PORT", "18737"))
    certfile = os.environ.get("PORTFOLIO_SSL_CERTFILE", "")
    keyfile = os.environ.get("PORTFOLIO_SSL_KEYFILE", "")
    server = ThreadingHTTPServer((host, port), partial(DocHandler, directory=ROOT))
    scheme = "http"
    if certfile and keyfile:
        # Terminate TLS here — no reverse proxy. LAN browsers reach this
        # directly (mkcert cert); floor the version at TLS 1.2.
        import ssl

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile, keyfile)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    print(f"portfolio server on {scheme}://{host}:{port} serving {ROOT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
