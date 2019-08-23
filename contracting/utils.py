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


# Standard method for hashing any data b into a hex string
def hash_bytes(b: bytes):
    h = hashlib.sha3_256()
    h.update(b)
    return h.hexdigest()


# Standard method for generating a transaction hash
def generate_tx_hash(tx_input: dict, tx_output: dict):
    encoded_input = encode(tx_input).encode()
    encoded_output = encode(tx_output).encode()

    return hash_bytes(encoded_input + encoded_output)


# Standard method for turning tx input and tx output into final data to be stored into a block
def make_finalized_tx(tx_input, tx_output):
    return {
        'input': tx_input,
        'output': tx_output,
        'hash': generate_tx_hash(tx_input, tx_output)
    }
