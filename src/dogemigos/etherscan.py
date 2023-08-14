import requests, datetime, json

def all_transactions(api_key, contract, start_block, end_block):
    data = {
        'module': 'account',
        'action': 'txlist',
        'address': contract,
        'startblock': str(start_block),
        'endblock':'99999999',
        'sort': 'asc',
        'apikey': api_key,
    }
    return requests.get("https://api.etherscan.io/api", data=data).json()['result']