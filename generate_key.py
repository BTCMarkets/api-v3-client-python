"""Generate your own Ed25519 key pair for a BTC Markets API key.

    python generate_key.py [btcmarkets_ed25519.pem]

Writes the private key to the file (readable only by you) and prints the public key.
Register the public key when creating the API key on the BTC Markets website; you get
back an API key id (``btcm_...``). The private key never leaves your machine.

You only need this if you want to generate the key pair yourself. If you let the
BTC Markets website generate it for you, skip this script.
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def private_key_pem(private_key):
    """The private key as unencrypted PKCS#8 PEM."""
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_jwk(private_key):
    """The public key as a JWK: the value you register with BTC Markets.

    ``x`` is the raw 32-byte public key, base64url without padding. It contains no secret.
    """
    raw = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return {
        'kty': 'OKP',
        'crv': 'Ed25519',
        'x': base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii'),
    }


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'btcmarkets_ed25519.pem'
    key = Ed25519PrivateKey.generate()

    # Create with owner-only permissions, and never overwrite an existing key.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(private_key_pem(key))

    print(f'Private key written to {path}. Keep it secret; never share it.')
    print('Public key to register on the BTC Markets website:')
    print(json.dumps(public_key_jwk(key)))
