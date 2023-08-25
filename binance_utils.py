import numpy as np
import pandas as pd
from binance import Client
from dotenv import dotenv_values


config = dotenv_values('.env')
client = Client(config.get('BINANCE_API_KEY'), config.get('BINANCE_API_SECRET'))


def get_all_coins():
    coins = client.get_all_coins_info()
    return [c['coin'] for c in coins]


def get_all_symbols():
    tickers = client.get_all_tickers()
    return [ticker['symbol'] for ticker in tickers]


def get_asset_balance(asset):
    asset_balance = client.get_asset_balance(asset.upper())
    free = asset_balance['free']
    locked = asset_balance['locked']
    return free, locked


def get_order_book(symbol='BTCUSDT'):
    orderbook = client.get_order_book(symbol=symbol)
    bids = orderbook['bids']
    asks = orderbook['asks']
    return bids, asks


def volume(denom='USDT'):
    data = [p for p in client.get_products()['data'] if p['q'] == denom]
    vols = {}
    for dic in data:
        if dic['cs']:
            vols[dic['b']] = dic['v'] * dic['c']
    vols = {k: v for k, v in sorted(vols.items(), key=lambda item: item[1], reverse=True)}
    return vols
