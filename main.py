import base64
import hashlib
import hmac
import time
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

base_url = 'https://api.btcmarkets.net'


def makeHttpCall(method, apiKey, privateKey, path, queryString, data=None):
    headers = buildHeaders(method, apiKey, privateKey, path, data)
    fullPath = ''
    if queryString is None:
        fullPath = path
    else:
        fullPath = path + '?' + queryString
    try:
        http_request = Request(base_url + fullPath, data, headers)

        if method == 'post' or method == 'put':
            response = urlopen(http_request, data)
        else:
            response = urlopen(http_request)

            return json.loads(str(response.read(), "utf-8"))
    except URLError as e:
        errObject = json.loads(e.read())
        if hasattr(e, 'code'):
            errObject['statusCode'] = e.code

        return errObject


def buildHeaders(method, apiKey, privateKey, path, data):
    now = str(int(time.time() * 1000))
    message = method + path + now
    if data is not None:
        message += data

    signature = signMessage(privateKey, message)

    headers = {
        "Accept": "application/json",
        "Accept-Charset": "UTF-8",
        "Content-Type": "application/json",
        "BM-AUTH-APIKEY": apiKey,
        "BM-AUTH-TIMESTAMP": now,
        "BM-AUTH-SIGNATURE": signature
    }

    return headers


def signMessage(privateKey, message):
    presignature = base64.b64encode(hmac.new(
        privateKey, message.encode('utf-8'), digestmod=hashlib.sha512).digest())
    signature = presignature.decode('utf8')

    return signature


class BTCMarkets:

    def __init__(self, apiKey, privateKey):
        self.apiKey = apiKey
        self.privateKey = base64.b64decode(privateKey)

    def get_orders(self):

        return makeHttpCall('GET', self.apiKey, self.privateKey, '/v3/orders', 'status=open')


api_key = 'add api key here'
private_key = 'add private key here'

client = BTCMarkets(api_key, private_key)

print(client.get_orders())

