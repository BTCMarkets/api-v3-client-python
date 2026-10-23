"""Call the BTC Markets API v3 with Ed25519 (default) or HMAC authentication.

    export BTCMARKETS_API_KEY=btcm_...
    export BTCMARKETS_PRIVATE_KEY="$(cat btcmarkets_ed25519.pem)"
    python main.py

For HMAC also set BTCMARKETS_AUTH_METHOD=HMAC; the private key is then the base64 secret.
"""
import os
import sys
from urllib.parse import urlparse

from auth import Ed25519Auth, HmacAuth
from btcmarkets_client import BTCMarketsClient, DEFAULT_BASE_URL

if __name__ == '__main__':
    api_key = os.getenv('BTCMARKETS_API_KEY')
    private_key = os.getenv('BTCMARKETS_PRIVATE_KEY')
    auth_method = os.getenv('BTCMARKETS_AUTH_METHOD', 'Ed25519')
    base_url = os.getenv('BTCMARKETS_BASE_URL', DEFAULT_BASE_URL)

    if not api_key or not private_key:
        sys.exit('Set BTCMARKETS_API_KEY and BTCMARKETS_PRIVATE_KEY (see README.md)')

    if auth_method == 'Ed25519':
        auth = Ed25519Auth(api_key, private_key, host=urlparse(base_url).hostname)
    else:
        auth = HmacAuth(api_key, private_key)

    client = BTCMarketsClient(auth, base_url)
    print(client.get_balances())
    # print(client.get_withdrawals())
    # print(client.get_orders())
    # print(client.place_sample_order())
    # print(client.cancel_order())
    # print(client.create_sample_withdrawal_request())
