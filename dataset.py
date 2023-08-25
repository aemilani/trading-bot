import os
import pandas as pd
import numpy as np
from binance import Client
from dotenv import dotenv_values
from datetime import datetime, timedelta
from dateutil.parser import parse


config = dotenv_values('.env')
binance_client = Client(config.get('BINANCE_API_KEY'), config.get('BINANCE_API_SECRET'))


class Dataset:
    def __init__(self) -> None:
        self.time_frames = [
            '1m',
            '2m',
            '3m',
            '5m',
            '15m',
            '30m',
            '1h',
            '2h',
            '4h',
            '6h',
            '8h',
            '12h',
            '1d',
            '3d',
            '1w',
            '1M'
        ]

    def get_data(self, ticker: str = 'BTCUSDT', interval: str = '1h', days_of_data: int = None,
                 start_date: str = None, end_date: str = None) -> pd.DataFrame():
        """
        Get candlestick data.
            :param ticker: The trading pair
            :param interval: Timeframe
            :param days_of_data: Days of data to get
            :param start_date: Should be provided if days_of_data is not provided
            :param end_date: Should be provided if days_of_data is not provided

            :return Candlestick DataFrame
        """
        if interval not in self.time_frames:
            raise ValueError(f'Supported timeframes: {self.time_frames}')
        if days_of_data:
            start_date = _get_start_time(days=days_of_data)
            klines = binance_client.get_historical_klines(ticker, interval, start_date)
        else:
            klines = binance_client.get_historical_klines(ticker, interval, start_date, end_date)
        data = _convert_to_dataframe(klines)
        return data

    def get_day_data(self, ticker: str = 'BTCUSDT', interval: str = '1h', date='2023-01-01'):
        if interval not in self.time_frames:
            raise ValueError(f'Supported timeframes: {self.time_frames}')
        start_date = parse(date)
        end_date = start_date + timedelta(minutes=1439)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        klines = binance_client.get_historical_klines(ticker, interval, start_date, end_date)
        data = _convert_to_dataframe(klines)
        return data


class TickDataset:
    def __init__(self) -> None:
        self.DATA_PATH = 'data/trades'

    def _load_data_file(self, filename):
        """Loads one data csv file."""
        df = pd.read_csv(os.path.join(self.DATA_PATH, filename), delimiter=',', index_col=0).set_index('time')
        df.index = pd.to_datetime(df.index, unit='ms', utc=True)
        return df

    def get_data(self, from_date: str, to_date: str, n_per_candle: int = 1000, divide_by: str = 'n_trades'):
        """Get tick dataset from from_date to and including to_date"""
        from_date = parse(from_date).date()
        to_date = parse(to_date).date()
        n_days = (to_date - from_date + timedelta(days=1)).days
        df = pd.DataFrame()
        for d in range(n_days):
            date = from_date + timedelta(days=d)
            filename = f'{date.__str__()}_BTCUSDT_binance_trades.csv'
            df = pd.concat([df, self._load_data_file(filename)])
        candles = pd.DataFrame()
        if divide_by == 'n_trades':
            for from_idx, to_idx in zip(range(0, len(df), n_per_candle), range(n_per_candle, len(df), n_per_candle)):
                candles = pd.concat([candles, _aggr(df.iloc[from_idx:to_idx])])
        elif divide_by == 'volume':
            cum_volume = df['qty'].cumsum()
            idxs = [0]
            for vol in range(n_per_candle, int(cum_volume.iloc[-1]), n_per_candle):
                idxs.append(np.argmax(cum_volume >= vol))
            idxs = list(set(idxs))
            idxs.sort()
            for from_idx, to_idx in zip(idxs, idxs[1:]):
                candles = pd.concat([candles, _aggr(df.iloc[from_idx:to_idx])])
        else:
            raise ValueError("Incorrect value entered for 'divide_by'. Correct values are 'n_trades' or 'volume'.")
        return candles


def _aggr(df):
    """Aggregates the input order dataframe into one data point."""
    new = {'time': df.index[-1], 'open': df['price'].iloc[0], 'high': df['price'].max(), 'low': df['price'].min(),
           'close': df['price'].iloc[-1], 'volume': df['qty'].sum(), 'avg_volume': df['qty'].mean(),
           'market_buy_volume': df[~ df['isBuyerMaker']]['qty'].sum(),
           'market_sell_volume': df[df['isBuyerMaker']]['qty'].sum(), 'first_id': df['aggrID'].iloc[0],
           'last_id': df['aggrID'].iloc[-1]}
    new = pd.DataFrame(new, index=[0])
    new = new.set_index('time', drop=True)
    return new


def _get_start_time(days: int) -> str:
    end = datetime.now()
    start = end - timedelta(days=days)
    start = start.strftime('%d %b, %Y')
    return start


def _convert_to_dataframe(klines) -> pd.DataFrame():
    data = pd.DataFrame(
        data=[row[1:11] for row in klines],
        columns=['open', 'high', 'low', 'close', 'volume', 'time', 'quote asset volume', 'number of trades',
                 'taker buy base asset volume', 'taker buy quote asset volume'],
    ).set_index('time')

    data.index = pd.to_datetime(np.round(data.index / 1000), unit='s')
    data = data.sort_index()
    data = data.apply(pd.to_numeric, axis=1)
    return data
