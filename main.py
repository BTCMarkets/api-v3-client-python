from btcmarkets_client import BTCMarketsClient
import os

if __name__ == "__main__":
    api_key = os.getenv('BTCMARKETS_API_KEY')
    private_key = os.getenv('BTCMARKETS_PRIVATE_KEY')
    if api_key is None or private_key is None:
        print("BTCMARKETS_API_KEY and BTCMARKETS_PRIVATE_KEY must be set")
        exit(1)
    btcmarkets_client = BTCMarketsClient(api_key, private_key)
    print (btcmarkets_client.get_withdrawals())
    #print(btcmarkets_client.create_sample_withdrawal_reqeust())
    #print(btcmarkets_client.get_orders())
    #print(btcmarkets_client.place_sample_order())
    #print(btcmarkets_client.cancel_order())


