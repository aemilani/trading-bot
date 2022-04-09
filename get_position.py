import numpy as np


def get_position(entry, sl, risk=0.01, max_pos_pct=0.1):
    """
    Calculate position size and leverage.
        :param entry: Entry price
        :param sl: Stop loss
        :param risk: Portion of portfolio risked
        :param max_pos_pct: Max position size (ratio of portfolio)

        :return pos_pct: Position size (ratio of portfolio)
        :return leverage: Leverage value
    """
    loss_pct = np.abs(entry - sl) / entry
    if loss_pct * max_pos_pct < risk:
        pos_pct = max_pos_pct
        leverage = int(np.floor(risk / (loss_pct * max_pos_pct)))
    else:
        leverage = 1
        pos_pct = risk / loss_pct
    return pos_pct, leverage


if __name__ =='__main__':
    entry = float(input('Entry:'))
    sl = float(input('Stop Loss:'))
    risk = float(input('Risk (percent of protfolio):')) / 100
    max_pos_pct = float(input('Max position size (percent of portfolio):')) / 100
    position = get_position(entry, sl, risk, max_pos_pct)
    print(f'\nPosition size (percent of portfolio): {position[0]}')
    print(f'Leverage: {position[1]}')
