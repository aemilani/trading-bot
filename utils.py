import json
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dateutil import parser
from functools import cache


@cache
def fib(n: int):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


def n_ticks_list():
    n_ticks = [fib(i) for i in range(13, 22)]
    n_ticks.extend([500, 1000, 1500, 4500])
    n_ticks.sort()
    return n_ticks


def json_print(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def fear_and_greed(n_data=0):
    """
    Get Crypto Fear and Greed Index data.
    :param n_data: Number of returned data. 0 --> all data.
    :return: A dictionary with 'data', 'dates', and 'timestamps' of the data, and 'time_until_update'.
    """
    response = requests.get(f'https://api.alternative.me/fng/?limit={n_data}')

    data = [int(dic['value']) for dic in response.json()['data']]
    timestamps = [int(dic['timestamp']) for dic in response.json()['data']]
    dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
    time_until_update = int(response.json()['data'][0]['time_until_update'])

    return {'data': data, 'dates': dates, 'timestamps': timestamps,
            'time_until_update': datetime.timedelta(seconds=time_until_update)}


def volume_profile(df, n_bins=10):
    df = df[['open', 'high', 'low', 'close', 'volume']]
    high = np.max(df['high'])
    low = np.min(df['low'])
    d_hl = high - low
    d = d_hl / n_bins
    coords = np.arange(low, high + 0.1, d)
    profile = pd.DataFrame(columns=['price', 'buy_volume', 'sell_volume', 'total_volume'])
    profile['price'] = pd.Series(coords).rolling(2).mean().dropna()
    buy_candles = df.where(df['close'] - df['open'] >= 0).dropna()
    sell_candles = df.where(df['close'] - df['open'] < 0).dropna()
    profile['buy_volume'] = np.histogram(buy_candles['close'], bins=coords, weights=buy_candles['volume'])[0]
    profile['sell_volume'] = np.histogram(sell_candles['close'], bins=coords, weights=sell_candles['volume'])[0]
    # profile['buy_volume'] = np.histogram((buy_candles['high'] + buy_candles['low']) / 2, bins=coords,
    #                                      weights=buy_candles['volume'])[0]
    # profile['sell_volume'] = np.histogram((sell_candles['high'] + sell_candles['low']) / 2, bins=coords,
    #                                       weights=sell_candles['volume'])[0]
    profile['total_volume'] = profile['buy_volume'] + profile['sell_volume']
    return profile


def get_daily_volume_profile(data, date, n_bins=50):
    """
    Calculates the volume profile for the given day
        Parameters:
            data (DataFrame): BTC 1m data
            date (str): The day for which the volume profile is to be calculated
            n_bins (int):  Number of bins in the volume profile histogram
        Returns:
            profile (DataFrame): BTC volume profile for the given day
    """
    idx_start = data[data['open_time'] == str(parser.parse(date))].index.values[0]
    idx_end = data[data['open_time'] == str(parser.parse(date) + datetime.timedelta(days=1))].index.values[0]
    day_data = data.iloc[idx_start:idx_end]
    profile = volume_profile(day_data, n_bins=n_bins)
    return profile


def get_poc_va(vp, va_ratio=0.95):
    total_vol = vp['total_volume'].sum()
    va_vol = va_ratio * total_vol

    poc_idx = vp.idxmax()['total_volume']
    poc = vp['price'].loc[poc_idx]

    cum_vol = vp.loc[poc_idx]['total_volume']
    curr_idx_high = poc_idx
    curr_idx_low = poc_idx
    while cum_vol < va_vol:
        if curr_idx_high <= (vp.index[-1] - 2):
            high_vol = vp.loc[curr_idx_high + 1:curr_idx_high + 2]['total_volume'].sum()
        else:
            high_vol = -1
        if curr_idx_low >= (vp.index[0] + 2):
            low_vol = vp.loc[curr_idx_low - 2:curr_idx_low - 1]['total_volume'].sum()
        else:
            low_vol = -1
        if high_vol >= low_vol:
            cum_vol += high_vol
            curr_idx_high += 2
        else:
            cum_vol += low_vol
            curr_idx_low -= 2
    va_high = vp.loc[curr_idx_high]['price']
    va_low = vp.loc[curr_idx_low]['price']

    return poc, va_high, va_low


def plot_volume_profile(profile, poc=None, va_high=None, va_low=None):
    plt.figure()
    plt.bar(profile['price'], profile['buy_volume'],
            width=profile['price'].iloc[-1] - profile['price'].iloc[-2], color='green')
    plt.bar(profile['price'], profile['sell_volume'],
            width=profile['price'].iloc[-1] - profile['price'].iloc[-2], color='orange', bottom=profile['buy_volume'])
    if poc:
        plt.axvline(poc, c='red')
    if va_high:
        plt.axvline(va_high, c='blue')
    if va_low:
        plt.axvline(va_low, c='blue')
    plt.show()
