import websocket, json, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_"+config.candle_length

candle_closes = []
trade_last_hr = False
current_open = 0

RSI_PERIOD = config.rsi_length
RSI_OVERSOLD = config.rsi_oversold_threshold
TRADE_SYMBOL = config.trade_pair
TRADE_QUANTITY = config.trade_quant

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(quantitiy, symbol, order_type = ORDER_TYPE_MARKET):
    try:
        print("order sent")
        order = client.create_order(symbol = symbol, type = order_type, quantity = quantity)
        print(order)
    except Exception as e:
        print("error- {}".format(e))
        return False
    return True

def crossed_above(series1, series2):
    if isinstance(series1, np.ndarry):
        series1 = pd.Series(series1)
    if isinstance(series2, (float, int, np.ndarry, np.integer, np.floating)):
        series2 = pd.Series(index=series1.index, data=series2)
    return  pd.Series((series1>series2) & (series1.shift(1) <= series2.shift(1)))


def on_open(ws):
    print('### opened ###')

def on_close(ws):
    print('### closed ###')

def on_message(ws, message):
    global candle_closes, trade_last_hr, current_open
    candle_stick = json.loads(message)
    candle = candle_stick['k']
    closed = candle['x']
    open = candle['o']
    close = candle['c']

    print("Price {}".format(close))

    if current_open != open:
        trade_last_hr = False
        current_open = open
        print("Open {}".format(open))

    if closed:
        candle_closes.append(float(close))
        print(candle_closes)

        if len(candle_closes) > RSI_PERIOD:
            np_closes = numpy.array(candle_closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("Last RSI: {}".format(rsi[-1]))

            if trade_last_hr == False:

                if crossed_above(rsi,RSI_OVERSOLD):
                    ordered = order(TRADE_QUANTITY, TRADE_SYMBOL)
                    if ordered:
                        trade_last_hr = True


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
