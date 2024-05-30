import base64
import hashlib
import hmac
import time
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

class BTCMarketsClient:
    def __init__(self, api_key, private_key):
        self.base_url = 'https://api.btcmarkets.net'
        self.api_key = api_key
        self.private_key = base64.b64decode(private_key)

    def get_orders(self):
        return self.__make_http_call('GET', self.api_key, self.private_key, '/v3/orders', 'status=all')

    def place_sample_order(self):
        payload = {
            'marketId': 'BTC-AUD',
            'price': '100.12',
            'amount': '0.0034',
            'type': 'Limit',
            'side': 'Bid'
        }
        return self.__make_http_call('POST', self.api_key, self.private_key, '/v3/orders', None, payload)

    def create_sample_withdrawal_reqeust(self):
        payload = {
            'assetName': 'USDT',
            'amount': '0.01',
            'toAddress': 'wrong address'
        }
        return self.__make_http_call('POST', self.api_key, self.private_key, '/v3/withdrawals', None, payload)


    def cancel_order(self):
        return self.__make_http_call('DELETE', self.api_key, self.private_key, '/v3/orders', 'id=1224905')

    def get_withdrawals(self):
        return self.__make_http_call('GET', self.api_key, self.private_key, '/v3/withdrawals', '')


    def __make_http_call(self, method, apiKey, privateKey, path, queryString, data=None):
        if data is not None:
            data = json.dumps(data)

        headers = self.___build_headers(method, apiKey, privateKey, path, data)
        if queryString is None:
            full_path = path
        else:
            full_path = path + '?' + queryString
        try:
            http_request = Request(self.base_url + full_path, data, headers, method=method)

            if method == 'POST' or method == 'PUT':
                response = urlopen(http_request, data = bytes(data, encoding="utf-8"))
            else:
                response = urlopen(http_request)

            return json.loads(str(response.read(), "utf-8"))
        except URLError as e:
            errObject = json.loads(e.read())
            if hasattr(e, 'code'):
                errObject['statusCode'] = e.code

            return errObject


    def ___build_headers(self, method, api_key, private_key, path, data):
        now = str(int(time.time() * 1000))
        message = method + path + now
        if data is not None:
            message += data

        signature = self.__sign_message(private_key, message)
        headers = {
            "Accept": "application/json",
            "Accept-Charset": "UTF-8",
            "Content-Type": "application/json",
            "BM-AUTH-APIKEY": api_key,
            "BM-AUTH-TIMESTAMP": now,
            "BM-AUTH-SIGNATURE": signature
        }
        return headers

    def __sign_message(self, private_key, message):
        signature = base64.b64encode(hmac.new(
            private_key, message.encode('utf-8'), digestmod=hashlib.sha512).digest())
        signature = signature.decode('utf8')
        return signature


