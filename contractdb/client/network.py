import zmq
from zcom import services

# Defaults

DEFAULT_SOCKET = services._socket('tcp://127.0.0.1:11111')

def get(socket_id: services.SocketStruct,
        msg: list,
        ctx: zmq.Context,
        timeout=500,
        linger=2000,
        retries=10,
        dealer=False):

    if retries < 0:
        return None

    if dealer:
        socket = ctx.socket(zmq.DEALER)
    else:
        socket = ctx.socket(zmq.REQ)

    socket.setsockopt(zmq.LINGER, linger)
    try:
        socket.connect(str(socket_id))
        socket.send_multipart(msg)
        response = socket.recv()
        socket.close()

        return response

    except Exception as e:
        socket.close()
        return get(socket_id, msg, ctx, timeout, linger, retries-1)


class ChainCmds:
    def __init__(self, socket_id=constants.DEFAULT_SOCKET, ctx=zmq.Context()):
        self.socket = socket_id
        self.ctx = ctx

    def server_call(self, msg):
        res = get(self.socket, msg, self.ctx)
        return res