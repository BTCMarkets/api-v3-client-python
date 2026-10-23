"""Authentication for the BTC Markets API v3.

Each class is one way to authenticate a request and exposes the same method::

    auth.headers(method, path, body) -> dict

``path`` is the request path without the query string and ``body`` is the exact JSON
string that will be sent (or ``None``). The HTTP client in ``btcmarkets_client.py``
merges the returned headers into the request.

* ``Ed25519Auth`` (recommended): a short-lived JWT signed with your Ed25519 private key,
  sent as ``Authorization: Bearer <jwt>``. BTC Markets holds only your public key.
* ``HmacAuth``: HMAC-SHA512 with a shared secret, sent in the ``BM-AUTH-*`` headers.
"""
import base64
import hashlib
import hmac
import json
import secrets
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class Ed25519Auth:
    """Sign each request with a JWT (``alg: EdDSA``).

    The token is bound to this one request: the HTTP method, the host and path, and a
    hash of the body. A captured token cannot be replayed against a different request
    and expires within seconds.

    * ``key_id`` - your API key id (``btcm_...``).
    * ``private_key`` - your Ed25519 private key as text, see ``load_private_key``.
    * ``host`` - the API host the token is for, e.g. ``api.btcmarkets.net``.
    """

    ISSUER = 'btcm-developer-platform'

    # The server rejects a token whose exp - iat is over 60 seconds, and allows only a
    # few seconds of clock skew: keep your clock synchronised (NTP).
    LIFETIME_SECONDS = 30

    def __init__(self, key_id, private_key, host):
        self.key_id = key_id
        self.private_key = load_private_key(private_key)
        self.host = host

    def headers(self, method, path, body):
        return {'Authorization': 'Bearer ' + self.request_jwt(method, path, body)}

    def request_jwt(self, method, path, body):
        """Build and sign the JWT for one request."""
        now = int(time.time())
        header = {'alg': 'EdDSA', 'typ': 'JWT', 'kid': self.key_id}
        claims = {
            'iss': self.ISSUER,
            'aud': self.host,
            'iat': now,
            'exp': now + self.LIFETIME_SECONDS,
            'jti': secrets.token_hex(16),  # unique per token
            # "<METHOD> <host><path>": upper-case method, no query string, no trailing slash.
            'uri': f'{method.upper()} {self.host}{path}',
        }
        if body:
            claims['body_hash'] = hashlib.sha256(body.encode('utf-8')).hexdigest()

        signing_input = _b64url(_json_bytes(header)) + '.' + _b64url(_json_bytes(claims))
        signature = self.private_key.sign(signing_input.encode('ascii'))
        return signing_input + '.' + _b64url(signature)


class HmacAuth:
    """Sign each request with HMAC-SHA512 over ``method + path + timestamp_ms + body``.

    * ``api_key`` - your API key.
    * ``secret`` - your base64-encoded API private key (the shared secret).
    """

    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = base64.b64decode(secret)

    def headers(self, method, path, body):
        now = str(int(time.time() * 1000))
        message = method + path + now + (body or '')
        digest = hmac.new(self.secret, message.encode('utf-8'), hashlib.sha512).digest()
        return {
            'BM-AUTH-APIKEY': self.api_key,
            'BM-AUTH-TIMESTAMP': now,
            'BM-AUTH-SIGNATURE': base64.b64encode(digest).decode('ascii'),
        }


def load_private_key(pem):
    """Parse an Ed25519 private key from PKCS#8 PEM (``-----BEGIN PRIVATE KEY-----``).

    This is the format shown by the BTC Markets website and written by ``generate_key.py``.
    The website shows the newlines as ``\\n``; both that and real newlines are accepted.
    """
    pem = pem.strip().replace('\\n', '\n')
    key = load_pem_private_key(pem.encode('utf-8'), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError('not an Ed25519 private key')
    return key


def _json_bytes(obj):
    return json.dumps(obj, separators=(',', ':')).encode('utf-8')


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')
