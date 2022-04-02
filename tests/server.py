"""This server is for test purpose."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import time
import os
import sys

path = os.path.dirname(os.path.realpath(__file__))

if len(sys.argv) < 2:
    print("Host and Port required")
else:
    hostName = sys.argv[1]
    serverPort = int(sys.argv[2])
    print(sys.argv)


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """Threading server."""

    pass


class MyServer(BaseHTTPRequestHandler):
    """Define the behavior of the server."""

    def do_GET(self):
        """All test request will be on this method."""
        if '?' in self.path:
            self.path = self.path.split('?')[0]

        if self.path in ['/', '/home', '/abc/']:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(path+'/index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path in ['/abc']:
            self.send_response(404)
            self.end_headers()
        elif self.path == '/error':
            self.send_response(500)
            self.end_headers()
        elif self.path == '/wait':
            time.sleep(3600)
        elif self.path == '/empty':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
        elif self.path == '/null':
            pass
        elif self.path == '/rss':
            self.send_response(200)
            self.send_header("Content-type", "application/rss+xml")
            self.end_headers()

            with open(path+'/data.rss', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(path+'/data.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/html/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(path+'/data2.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.replace('/', '').isdigit():
            self.send_response(int(self.path.replace('/', '')))
            self.send_header("Content-type", "text/html")
            self.end_headers()
        elif self.path == '/good':
            self.send_response(301)
            self.send_header('Location', '/201')
            self.end_headers()
        elif self.path == '/bad':
            self.send_response(301)
            self.send_header('Location', '/401')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        """Permit to check the availability of the test server."""
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    server = ThreadingSimpleServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")
