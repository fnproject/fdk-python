import asyncio
import h11
import os

class HTTPProtocol(asyncio.Protocol):

    def __init__(self):
        self.connection = h11.Connection(h11.SERVER)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.connection.receive_data(data)
        while True:
            event = self.connection.next_event()
            if isinstance(event, h11.Request):
                self.send_response(event)
            elif (
                isinstance(event, h11.ConnectionClosed)
                or event is h11.NEED_DATA or event is h11.PAUSED
            ):
                break
        if self.connection.our_state is h11.MUST_CLOSE:
            self.transport.close()

    def send_response(self, event):
        body = b"%s %s" % (event.method.upper(), event.target)
        headers = [
            ('content-type', 'text/plain'),
            ('content-length', str(len(body))),
        ]
        response = h11.Response(status_code=200, headers=headers)
        self.send(response)
        self.send(h11.Data(data=body))
        self.send(h11.EndOfMessage())

    def send(self, event):
        data = self.connection.send(event)
        self.transport.write(data)

async def main():
    socket_path = '/tmp/iofs/lsnr.sock'
    phony_socket_path = '/tmp/iofs/phony.sock'

    loop = asyncio.get_running_loop()
    server = await loop.create_unix_server(HTTPProtocol, path=phony_socket_path)

    # fix perms on sock and symlink to real sock
    os.chmod(phony_socket_path, 0o666)
    os.symlink(os.path.basename(phony_socket_path), socket_path)

    await server.serve_forever()

asyncio.run(main())
