import asyncio
import zmq
import zmq.asyncio
from contractdb.interfaces import StateInterface
from contractdb.chain import SQLLiteBlockStorageDriver
from contractdb.engine import Engine
from contractdb.driver import ContractDBDriver
from contracting.compilation.compiler import ContractingCompiler
from contracting.db.encoder import encode, decode

import logging


class Server:
    def __init__(self, port: int, ctx: zmq.Context=zmq.asyncio.Context(), linger=2000, poll_timeout=2000):
        self.port = port

        self.address = 'tcp://*:{}'.format(port)

        self.ctx = ctx

        self.socket = None

        self.linger = linger
        self.poll_timeout = poll_timeout

        self.running = False

        self.interface = StateInterface(driver=ContractDBDriver(),
                                        compiler=ContractingCompiler(),
                                        engine=Engine(),
                                        blocks=SQLLiteBlockStorageDriver())

        self.log = logging.getLogger('Server')
        self.log.info("Server init")

    async def serve(self):
        self.log.info("ContractDB server is starting .. ")

        self.setup_socket()

        self.running = True

        while self.running:
            try:
                event = await self.socket.poll(timeout=self.poll_timeout, flags=zmq.POLLIN)
                if event:
                    m = await self.socket.recv_multipart()
                    self.log.info(f'got {m}')
                    _id = m[0]
                    msg = m[1]
                    self.log.info("id : {}".format(_id))
                    self.log.info("msg : {}".format(msg))
                    asyncio.ensure_future(self.handle_msg(_id, msg))
                    await asyncio.sleep(0)

            except zmq.error.ZMQError:
                self.log.info('zmq error: {}'.format(zmq.error.ZMQError))
                self.socket.close()
                self.setup_socket()

        self.socket.close()

    async def handle_msg(self, _id, msg):
        # Try to deserialize the message and run it through the rpc service
        try:
            json_command = decode(msg.decode())

            self.log.info('Received command: {}'.format(json_command))

            result = self.interface.process_json_rpc_command(json_command)

        # If this fails, just set the result to None
        except Exception as e:
            self.log.info('EXCEPTION!! -> ', str(e))
            result = None

        # Try to send the message now. This persists if the socket fails.
        sent = False
        while not sent:
            try:
                msg = encode(result).encode()

                self.log.info('result sent: {}, {}'.format(msg, result))
                await self.socket.send_multipart([_id, msg])
                sent = True

            except zmq.error.ZMQError:
                self.log.info('zmq error: {}'.format(zmq.error.ZMQError))
                self.socket.close()
                self.setup_socket()

    def setup_socket(self):
        self.socket = self.ctx.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.LINGER, self.linger)
        self.socket.bind(self.address)

    def stop(self):
        self.running = False


def start_server(port=2020, ctx=zmq.asyncio.Context()):
    server = Server(port=port, ctx=ctx)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve())
    loop.close()
