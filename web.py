import hashlib
import os
import sys
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs


def run(file):
    auth_param = hashlib.sha256(os.urandom(32)).hexdigest()
    class ServeResultsHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            query = urlparse(self.path).query
            query_components = parse_qs(query)

            if query_components.get("key", "") != [auth_param]:
                return None
            self.path = file
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        def log_message(self, format, *args):
            pass


    [addr, port] = os.environ.get(
        "SECRETMAGPIE_LISTEN_ADDR", "127.0.0.1:8080"
    ).split(":")

    with socketserver.TCPServer((addr, int(port)), ServeResultsHandler) as httpd:
        print(
            f"Available at http://{addr}:{port}/?key={auth_param}"  # nosec hardcoded_bind_all_interfaces
        )
        # Force a flush of stdout at this point
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
            httpd.server_close()
            print("Server shutdown.")
