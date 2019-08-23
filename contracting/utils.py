import nacl.signing
from .db.encoder import encode
import hashlib


def make_tx(key: nacl.signing.SigningKey, contract, func, arguments):
    tx = {
        'sender': key.verify_key.encode().hex(),
        'signature': None,
        'payload': {
            'contract': contract,
            'function': func,
            'arguments': arguments
        }
    }

    message = encode(tx['payload']).encode()

    signature = key.sign(message)[:64]

    tx['signature'] = signature.hex()

    return tx


def hash_bytes(b: bytes):
    h = hashlib.sha3_256
    h.update(b)
    return h.digest()


def generate_tx_hash(tx_input, tx_output):
    encoded_input = encode(tx_input)
    encoded_output = encode(tx_output)

    return hash_bytes(encoded_input + encoded_output)


def make_finalized_tx(tx_input, tx_output):
    return {
        'input': tx_input,
        'output': tx_output,
        'hash': generate_tx_hash(tx_input, tx_output)
    }
