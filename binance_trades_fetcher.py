import os
import time
import requests
import calendar
import pandas as pd
from datetime import datetime, timedelta
from dateutil.parser import parse


def get_unix_ms_from_date(date):
    return int(calendar.timegm(date.timetuple()) * 1000 + date.microsecond / 1000)


def get_first_trade_id_from_start_date(symbol, from_date):
    new_end_date = from_date + timedelta(seconds=60)
    r = requests.get('https://api.binance.com/api/v3/aggTrades',
                     params={
                         "symbol": symbol,
                         "startTime": get_unix_ms_from_date(from_date),
                         "endTime": get_unix_ms_from_date(new_end_date)
                     })

    if r.status_code != 200:
        print(f'API request error. Request status code: {r.status_code}')
        print('Sleeping for 10s...')
        time.sleep(10)
        get_first_trade_id_from_start_date(symbol, from_date)

    response = r.json()
    if len(response) > 0:
        return response[0]['a']
    else:
        raise Exception('no trades found')


def get_trades(symbol, from_id):
    r = requests.get("https://api.binance.com/api/v3/aggTrades",
                     params={
                         "symbol": symbol,
                         "limit": 1000,
                         "fromId": from_id
                     })

    if r.status_code != 200:
        print(f'API request error. Request status code: {r.status_code}')
        print('Sleeping for 10s...')
        time.sleep(10)
        get_trades(symbol, from_id)

    return r.json()


def trim(df, limit_date):
    return df[df['T'] <= get_unix_ms_from_date(limit_date)]


def fetch_binance_trades(symbol, date):
    symbol = symbol.upper()
    from_date = parse(date)
    to_date = from_date + timedelta(days=1) - timedelta(microseconds=1)

    from_id = get_first_trade_id_from_start_date(symbol, from_date)
    current_time = 0
    df = pd.DataFrame()

    while current_time < get_unix_ms_from_date(to_date):
        try:
            trades = get_trades(symbol, from_id)

            from_id = trades[-1]['a']
            current_time = trades[-1]['T']

            print(
                f'fetched {len(trades)} trades from id {from_id} @ {datetime.utcfromtimestamp(current_time / 1000.0)}')

            df = pd.concat([df, pd.DataFrame(trades)])

            # don't exceed request limits
            time.sleep(0.5)
        except Exception:
            print('Exception thrown.')
            print('Sleeping for 15 seconds...')
            time.sleep(15)

    df.drop_duplicates(subset='a', inplace=True)
    df = trim(df, to_date)
    df.columns = ['aggrID', 'price', 'qty', 'firstID', 'lastID', 'time', 'isBuyerMaker', 'isBestMatch']

    filename = f'data/trades/{str(from_date.date())}_{symbol}_binance_trades.csv'
    df.to_csv(filename)

    print(f'{filename} file created!')


def _check_trades_file(file_path):
    df = pd.read_csv(file_path)
    ids = df['aggrID'].to_numpy()
    for i in range(len(ids) - 1):
        if ids[i + 1] - ids[i] != 1:
            print(f'Inconsistent data at ID = {ids[i + 1]}')
            return
    print('Dataset OK!')


def check_trades_files(data_folder):
    for file in os.listdir(data_folder):
        print(f'Checking {file} ...')
        path = os.path.join(data_folder, file)
        _check_trades_file(path)


if __name__ == '__main__':
    for day in range(1, 11):
        fetch_binance_trades('BTCUSDT', f'2023-04-{day}')
