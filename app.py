from flask import Flask, render_template, jsonify
from dataset import TickDataset


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/history")
def history():
    ticks = TickDataset().get_data('2022-04-16', '2022-04-16').reset_index()
    ticks = ticks.loc[:, ['time', 'open', 'high', 'low', 'close']]
    ticks['time'] = ticks['time']
    candles = []
    for idx, row in ticks.iterrows():
        candles.append({
            'time': row['time'],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close']})
    return jsonify(candles)


@app.route("/buy")
def buy():
    return 'buy'


@app.route("/sell")
def sell():
    return 'sell'


@app.route("/settings")
def settings():
    return 'settings'
