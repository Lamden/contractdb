import zmq
import time
from zcomm import services
from contracting.db.encoder import encode, decode

import logging

# Defaults

DEFAULT_SOCKET = services._socket('tcp://127.0.0.1:2020')


def get(socket_id: services.SocketStruct,
        msg: dict,
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
        #time.sleep(5)
        emsg = encode(msg).encode()
        #print("encoded msg :", emsg)
        socket.send(emsg)
        #print("waiting for rcv")
        response = socket.recv()
        #print("rcv msg ->", response)
        dres = decode(response.decode())
        socket.close()

        return dres

    except Exception as e:
        print(e)
        socket.close()
        return get(socket_id, msg, ctx, timeout, linger, retries-1, dealer=True)


class ChainCmds:
    def __init__(self, socket_id=DEFAULT_SOCKET, ctx=zmq.Context()):
        self.log = logging.getLogger('Client')

        self.socket = socket_id
        self.ctx = ctx

    def server_call(self, msg: dict):
        self.log.info("Server call msg -> {}".format(msg))
        res = get(self.socket, msg, self.ctx, retries=0, dealer=True)
        self.log.info("Server Res {}".format(res))
        return res