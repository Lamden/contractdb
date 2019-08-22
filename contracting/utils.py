import nacl.signing
import json
from .db.encoder import encode

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
