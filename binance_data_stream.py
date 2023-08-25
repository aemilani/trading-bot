import json
import time
import multiprocessing
from websocket import WebSocketApp
from binance_utils import get_order_book


# Define the on_message functions for the two websockets
def on_message_trades(wsapp, message):
    with open("data/trades.txt", "a") as f:
        f.write(message + "\n")


def on_message_orderbook(wsapp, message):
    with open("data/orderbook.txt", "a") as f:
        f.write(message + "\n")


# Define the functions that will be run as separate processes
def run_trades_websocket():
    wsapp = WebSocketApp(trade_endpoint, on_message=on_message_trades)
    wsapp.run_forever()


def run_orderbook_websocket():
    wsapp = WebSocketApp(orderbook_endpoint, on_message=on_message_orderbook)
    wsapp.run_forever()


def get_current_orderbook():
    while True:
        next_call = time.time()
        with open("data/orderbook.txt", "a") as f:
            bids, asks = get_order_book()
            f.write(json.dumps({'t': int(1000 * time.time()), 'b': bids, 'a': asks}) + "\n")
        next_call += 1
        time.sleep(next_call - time.time())


# Define the endpoints for the two websockets
trade_endpoint = 'wss://stream.binance.com:9443/ws/btcusdt@aggTrade'
orderbook_endpoint = 'wss://stream.binance.com:9443/ws/btcusdt@depth10@1000ms'


if __name__ == '__main__':
    # Create two separate processes for the two websockets
    trades_process = multiprocessing.Process(target=run_trades_websocket)
    orderbook_process = multiprocessing.Process(target=run_orderbook_websocket())

    # Start both processes
    trades_process.start()
    orderbook_process.start()

    # Wait for both processes to finish
    trades_process.join()
    orderbook_process.join()
