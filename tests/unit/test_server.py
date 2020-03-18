from unittest import TestCase
from contractdb.server import Server
import asyncio
import zmq
import json


async def stop_server(s, timeout):
    await asyncio.sleep(timeout)
    s.stop()


async def get(msg, ctx, _json=True):
    socket = ctx.socket(zmq.DEALER)
    socket.connect('tcp://127.0.0.1:2020')

    if _json:
        await socket.send_json(msg)
    else:
        await socket.send(msg)

    res = await socket.recv()

    res = json.loads(res)

    return res


class TestServer(TestCase):
    def setUp(self):
        self.ctx = zmq.asyncio.Context()

    def tearDown(self):
        self.ctx.destroy()

    def test_init(self):
        Server(port=2020, ctx=self.ctx)

    def test_addresses_correct(self):
        m = Server(port=2020, ctx=self.ctx)

        self.assertEqual(m.address, 'tcp://*:2020')

    def test_sockets_are_initially_none(self):
        m = Server(port=2020, ctx=self.ctx)

        self.assertIsNone(m.socket)

    def test_setup_frontend_creates_socket(self):
        m = Server(port=2020, ctx=self.ctx)
        m.setup_socket()

        self.assertEqual(m.socket.type, zmq.ROUTER)
        self.assertEqual(m.socket.getsockopt(zmq.LINGER), m.linger)

    def test_serve_starts_loop(self):
        m = Server(port=2020, ctx=self.ctx)

        tasks = asyncio.gather(
            m.serve(),
            stop_server(m, 0.2),
        )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)

    def test_sending_command_returns_correctly(self):
        # Setup server
        m = Server(port=2020, ctx=self.ctx)

        # Setup contract to get
        contract = '''
def stu():
    print('howdy partner')
        '''

        name = 'stustu'

        m.interface.driver.set_contract(name, contract)

        command = {'command': 'get_contract',
                   'arguments': {
                       'name': 'stustu'
                   }}

        tasks = asyncio.gather(
            m.serve(),
            get(command, self.ctx, _json=True),
            stop_server(m, 0.2),
        )

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(tasks)[1]

        expected = m.interface.get_contract('stustu')

        self.assertEqual(res, expected)

    def test_sending_bad_command_returns_none_results(self):
        # Setup server
        m = Server(port=2020, ctx=self.ctx)

        tasks = asyncio.gather(
            m.serve(),
            get(b'', self.ctx, _json=False),
            stop_server(m, 0.2),
        )

        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(tasks)[1]

        self.assertIsNone(res)
