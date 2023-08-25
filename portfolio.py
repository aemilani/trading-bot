import numpy as np
import pandas as pd


class Portfolio:
    def __init__(self, start_cash=1000, max_pos_pct=0.1, max_leverage=100,
                 maker_fee=0.0002, taker_fee=0.00055):
        """
        Initialize the portfolio.
            :param start_cash: Initial balance
            :param max_pos_pct: Max position size (ratio of portfolio)
            :param max_leverage: Max position leverage
            :param maker_fee: Limit order fee
            :param taker_fee: Market order fee
        """
        self.balance = start_cash
        self.max_pos_pct = max_pos_pct
        self.max_leverage = max_leverage
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee

        self.trade = pd.DataFrame.from_dict({'position': ['flat'], 'size': [None], 'open_date': [None],
                                             'close_date': [None], 'entry': [None], 'sl': [None], 'tp': [None],
                                             'result': [None], 'balance': [None]})
        self.trade_ts = pd.DataFrame(
            columns=['position', 'size', 'open_date', 'close_date', 'entry', 'sl', 'tp', 'result', 'balance'])

    def open_trade(self, entry, sl, tp, date, risk=0.01, lev=None):
        """
        Open position (market).
        :param entry: Entry price
        :param sl: Initial stop loss price
        :param tp: Initial take profit price
        :param date: Trade open date (datetime object)
        :param risk: Portion of portfolio risked
        :param lev: Leverage
        :return: None
        """
        if lev:
            pos_pct, leverage = self.max_pos_pct, lev
            if leverage > self.max_leverage:
                return None
            size = pos_pct * self.balance * leverage
            fee = size * self.taker_fee
            self.balance -= fee
            self.trade = pd.DataFrame()
            pos = 'short' if sl > entry else 'long'
            self.trade = pd.DataFrame.from_dict({'position': [pos], 'size': [size], 'open_date': [date],
                                                 'close_date': [None], 'entry': [entry], 'sl': [sl], 'tp': [tp],
                                                 'result': [None], 'balance': [None]})
        else:
            pos_pct, leverage = self.get_position(entry, sl, risk)
            if leverage > self.max_leverage:
                return None
            size = pos_pct * self.balance * leverage
            fee = size * self.taker_fee
            self.balance -= fee
            self.trade = pd.DataFrame()
            pos = 'short' if sl > entry else 'long'
            self.trade = pd.DataFrame.from_dict({'position': [pos], 'size': [size], 'open_date': [date],
                                                 'close_date': [None], 'entry': [entry], 'sl': [sl], 'tp': [tp],
                                                 'result': [None], 'balance': [None]})

    def stop_loss(self, sl, date):
        """
        Trigger stop loss (market).
        :param sl: Stop loss price
        :param date: Stop loss date
        :return: None
        """
        fee = self.trade.loc[0, 'size'] * self.taker_fee
        self.balance -= fee
        self.balance -= \
            np.abs(self.trade.loc[0, 'entry'] - sl) / self.trade.loc[0, 'entry'] * self.trade.loc[0, 'size']
        self.trade.loc[0, 'close_date'] = date
        self.trade.loc[0, 'sl'] = sl
        self.trade.loc[0, 'result'] = 'lose'
        self.trade.loc[0, 'balance'] = self.balance
        self.trade_ts = pd.concat([self.trade_ts, self.trade]).reset_index(drop=True)
        self.trade = pd.DataFrame.from_dict({'position': ['flat'], 'size': [None], 'open_date': [None],
                                             'close_date': [None], 'entry': [None], 'sl': [None], 'tp': [None],
                                             'result': [None], 'balance': [None]})

    def take_profit(self, tp, date, order_type='limit'):
        """
        Trigger take profit (limit).
        :param tp: Take profit price
        :param date: Stop loss date
        :param order_type: 'market' or 'limit'
        :return: None
        """
        if order_type == 'limit':
            fee = self.trade.loc[0, 'size'] * self.maker_fee
        else:
            fee = self.trade.loc[0, 'size'] * self.taker_fee
        self.balance -= fee
        self.balance += \
            np.abs(self.trade.loc[0, 'entry'] - tp) / self.trade.loc[0, 'entry'] * self.trade.loc[0, 'size']
        self.trade.loc[0, 'close_date'] = date
        self.trade.loc[0, 'tp'] = tp
        self.trade.loc[0, 'result'] = 'win'
        self.trade.loc[0, 'balance'] = self.balance
        self.trade_ts = pd.concat([self.trade_ts, self.trade]).reset_index(drop=True)
        self.trade = pd.DataFrame.from_dict({'position': ['flat'], 'size': [None], 'open_date': [None],
                                             'close_date': [None], 'entry': [None], 'sl': [None], 'tp': [None],
                                             'result': [None], 'balance': [None]})

    def get_position(self, entry, sl, risk):
        """
        Calculate position size and leverage.
            :param entry: Entry price
            :param sl: Stop loss
            :param risk: Portion of portfolio risked

            :return pos_pct: Position size (ratio of balance)
            :return leverage: Leverage value
        """
        loss_pct = np.abs(entry - sl) / entry
        if loss_pct * self.max_pos_pct < risk:
            pos_pct = self.max_pos_pct
            leverage = int(np.floor(risk / (loss_pct * self.max_pos_pct)))
        else:
            leverage = 1
            pos_pct = risk / loss_pct
        return pos_pct, leverage
