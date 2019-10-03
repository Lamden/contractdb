import asyncio
import zmq
import zmq.asyncio
from contractdb.server.interfaces import StateInterface
from contractdb.db.chain import SQLLiteBlockStorageDriver
from contractdb.execution.executor import Engine
from contractdb.db.driver import ContractDBDriver
from contracting.compilation.compiler import ContractingCompiler
from contracting.db.encoder import encode, decode


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

    async def serve(self):
        self.setup_socket()

        self.running = True

        while self.running:
            try:
                event = await self.socket.poll(timeout=self.poll_timeout, flags=zmq.POLLIN)
                if event:
                    _id = await self.socket.recv()
                    msg = await self.socket.recv()
                    asyncio.ensure_future(self.handle_msg(_id, msg))
                    await asyncio.sleep(0)

            except zmq.error.ZMQError:
                self.socket.close()
                self.setup_socket()

        self.socket.close()

    async def handle_msg(self, _id, msg):
        # Try to deserialize the message and run it through the rpc service
        try:
            json_command = decode(msg.decode())
            print('Got: {}'.format(json_command))
            result = self.interface.process_json_rpc_command(json_command)
            print('Returning: {}'.format(result))

        # If this fails, just set the result to None
        except Exception as e:
            print(str(e))
            result = None

        # Try to send the message now. This persists if the socket fails.
        sent = False
        while not sent:
            try:
                msg = encode(result).encode()

                await self.socket.send_multipart([_id, msg])
                sent = True

            except zmq.error.ZMQError:
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
