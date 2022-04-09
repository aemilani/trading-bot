import pandas as pd
import numpy as np
from binance import Client
from dotenv import dotenv_values
from datetime import datetime, timedelta


config = dotenv_values('.env')
client = Client(config.get('BINANCE_API_KEY'), config.get('BINANCE_API_SECRET'))


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

    def get_data(self, ticker: str, tf: str, days: int) -> pd.DataFrame():
        """
        Get candlestick data.
            :param ticker: The trading pair
            :param tf: Timeframe
            :param days: Days of data to get

            :return Candlestick DataFrame
        """
        return self._download_data(ticker=ticker, tf=tf, days=days)

    def _download_data(self, ticker: str = 'BTCUSDT', tf: str = '1h', days: int = 10) -> pd.DataFrame():
        if tf not in self.time_frames:
            raise ValueError(f'Supported timeframes: {self.time_frames}')
        start_date = _get_start_time(days=days)
        klines = client.get_historical_klines(ticker, tf, start_date)
        data = _convert_to_dataframe(klines)
        data['symbol'] = ticker
        return data


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
