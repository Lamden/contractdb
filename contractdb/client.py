from zcomm import services
from rocks import constants
import zmq

from contracting.db.encoder import encode, decode


def get(socket_string,
        msg,
        ctx: zmq.Context,
        timeout=500,
        linger=2000,
        retries=10):

    if retries < 0:
        return None

    socket = ctx.socket(zmq.DEALER)

    socket.setsockopt(zmq.LINGER, linger)
    try:
        socket.connect(socket_string)

        socket.send(msg)
        response = decode(socket.recv())
        socket.close()

        return response

    except Exception as e:
        socket.close()
        return get(socket_string, msg, ctx, timeout, linger, retries-1)


class ContractDBClient:
    def __init__(self, socket_string, ctx=zmq.Context()):
        self.socket = socket_string
        self.ctx = ctx

    def server_call(self, msg):
        res = get(self.socket, msg, self.ctx)
        return res

    def build_command(self, command_name, **kwargs):
        command_dict = {
            'command': command_name,
            'arguments': kwargs
        }

        encoded_command = encode(command_dict)
        return encoded_command.encode()

    def ping(self):
        msg = self.build_command('ping')
        return self.server_call(msg)

    def run(self, transaction):
        msg = self.build_command('run', transaction=transaction)
        return self.server_call(msg)

    def run_all(self, transactions):
        msg = self.build_command('run_all', transactions=transactions)
        return self.server_call(msg)

    def get_var(self, contract, variable, key):
        msg = self.build_command('get_var', contract=contract, variable=variable, key=key)
        return self.server_call(msg)

    def get_vars(self, contract):
        msg = self.build_command('get_vars', contract=contract)
        return self.server_call(msg)

    def get_contract(self, contract):
        msg = self.build_command('get_contract', contract=contract)
        return self.server_call(msg)

    def lint(self, code):
        msg = self.build_command('lint', code=code)
        return self.server_call(msg)

    def compile(self, code):
        msg = self.build_command('compile', code=code)
        return self.server_call(msg)

    def get_block_by_hash(self, h):
        msg = self.build_command('get_block_by_hash', h=h)
        return self.server_call(msg)

    def get_block_by_index(self, i):
        msg = self.build_command('get_block_by_index', i=i)
        return self.server_call(msg)

    def get_transaction_by_hash(self, h):
        msg = self.build_command('get_transaction_by_hash', h=h)
        return self.server_call(msg)

    def block_height(self, h):
        msg = self.build_command('block_height')
        return self.server_call(msg)

    def block_hash(self, h):
        msg = self.build_command('block_hash')
        return self.server_call(msg)
