"""A minimal HTTP client for the BTC Markets API v3.

It sends the request and attaches the headers from an authentication scheme in
``auth.py``, so the same calls work with either scheme::

    client = BTCMarketsClient(Ed25519Auth(key_id, private_key, 'api.btcmarkets.net'))
    client = BTCMarketsClient(HmacAuth(api_key, secret))
"""
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = 'https://api.btcmarkets.net'


class BTCMarketsClient:
    def __init__(self, auth, base_url=DEFAULT_BASE_URL):
        self.auth = auth
        self.base_url = base_url.rstrip('/')

    def get_orders(self):
        return self.request('GET', '/v3/orders', 'status=all')

    def place_sample_order(self):
        return self.request('POST', '/v3/orders', body={
            'marketId': 'BTC-AUD',
            'price': '100.12',
            'amount': '1.034',
            'type': 'Limit',
            'side': 'Bid',
        })

    def cancel_order(self):
        return self.request('DELETE', '/v3/orders', 'id=1224905')

    def get_withdrawals(self):
        return self.request('GET', '/v3/withdrawals')

    def create_sample_withdrawal_request(self):
        return self.request('POST', '/v3/withdrawals', body={
            'assetName': 'USDT',
            'amount': '0.01',
            'toAddress': 'wrong address',
        })

    def request(self, method, path, query_string=None, body=None):
        """Make one authenticated request and return the parsed JSON response.

        ``path`` is the request path without the query string (e.g. ``/v3/orders``);
        this is what gets signed. ``query_string`` (e.g. ``status=all``) is appended to
        the URL only. On an HTTP error the error body is returned with ``statusCode`` added.
        """
        # Serialise once: the exact string that is signed must be the one that is sent.
        data = json.dumps(body) if body is not None else None

        headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'UTF-8',
            'Content-Type': 'application/json',
            'User-Agent': 'btcmarkets-api-v3-client-python',
        }
        headers.update(self.auth.headers(method, path, data))

        url = self.base_url + path + ('?' + query_string if query_string else '')
        http_request = Request(url, data.encode('utf-8') if data else None, headers, method=method)
        try:
            with urlopen(http_request) as response:
                return json.loads(response.read() or b'{}')
        except HTTPError as e:
            error = json.loads(e.read() or b'{}')
            error['statusCode'] = e.code
            return error
