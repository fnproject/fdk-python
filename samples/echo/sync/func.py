import socketserver
import os
from http.server import BaseHTTPRequestHandler

class UnixHTTPServer(socketserver.UnixStreamServer):
    def get_request(self):
        request, client_address = self.socket.accept()
        # BaseHTTPRequestHandler expects a tuple with the client address at index
        # 0, so we fake one
        if len(client_address) == 0:
          client_address = (self.server_address,)
        return (request, client_address)

class myHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # XXX(reed)
        # body = self.rfile.read(int(self.headers.getheader('Content-Length')))

        self.send_response(200)
        self.send_header('Content-Type','text/ascii')
        self.end_headers()
        self.wfile.write("yo yo yo!")
        return

if __name__ == "__main__":
    socket_path = '/tmp/iofs/lsnr.sock'
    phony_socket_path = '/tmp/iofs/phony.sock'
    try:
        with UnixHTTPServer(phony_socket_path, myHandler, False) as server:
            server.server_bind()
            os.chmod(phony_socket_path, 0o666)
            os.symlink(os.path.basename(phony_socket_path), socket_path)
            server.server_activate()
            server.serve_forever()
    except Exception as ex:
        print(ex)
