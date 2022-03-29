from binance.spot import Spot
from requests.sessions import Session
import random
from datetime import datetime, timedelta, tzinfo
import json
import time
from tqdm import tqdm
from secret import my_api_key, my_api_secret
api_key = input('Please enter your Binance api key:') or my_api_key
api_secret = input('Please enter your Binance api secret:') or my_api_secret

client = Spot(api_key, api_secret)

def pprint(string):
    print(json.dumps(string, indent=4, ensure_ascii=False))

class UTC(tzinfo):
    """UTC"""

    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)

cli = Spot(key=api_key, secret=api_secret)

def getAllMarketPairs():
    while True:
        try:
            symbols = cli.exchange_info()['symbols']
            break
        except:
            pass
    pairs = {}
    for symbol in symbols:
        pairs[symbol['symbol']] = {'baseAsset': symbol['baseAsset'],
                                   'quoteAsset': symbol['quoteAsset']}
    return pairs


def getHistoryTrade(pairs, useJsonFile = ' '):
    if useJsonFile != ' ':
        with open(useJsonFile, 'r') as f:
            return json.load(f)
    total_trades = []
    used_symbols = []
    print('Collecting your trading history...')
    progress = tqdm(total=len(pairs.keys()))
    for pair in pairs.keys():
        while True:
            try:
                sym_trade = cli.my_trades(pair)
                time.sleep(random.random() / 2)
                break
            except:
                time.sleep(10)
        if len(sym_trade) > 0:
            used_symbols.append(sym_trade)
            # pprint(sym_trade)
        total_trades += sym_trade
        progress.update(1)
    return total_trades


def BFS(graph, start, end):
    if start == end:
        return True, {}
    visited = set()
    queue = []
    visited.add(start)
    queue.append(start)
    pred = {}
    while queue:          # Creating loop to visit each node
        m = queue.pop(0)

        for neighbour in graph[m].keys():
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
                pred[neighbour] = m
                if neighbour == end:
                    return True, pred
    return False, {}


def build_fee_dict(fee_list):
    fee_dict = {}
    for fee in fee_list:
        fee_dict[fee['symbol']] = {
            "maker": fee["makerCommission"], 'taker': fee["takerCommission"]}
    return fee_dict


def build_price_dict(price_list):
    price_dict = {}
    for price in price_list:
        price_dict[price['symbol']] = price['price']
    return price_dict


def get_BFS_path(pred, start, end):
    if start == end:
        return []
    path_rev = []
    while end != start:
        path_rev.append(end)
        end = pred[end]
    path_rev.append(end)
    path_rev.reverse()
    return path_rev


def show_current_earn(graph, start='ETH', end='USDT'):
    def find_detail(base, quote):
        return graph[base][quote]

    res, pred = BFS(graph, start, end)
    if res:
        path = get_BFS_path(pred, start, end)
        # print(path)
        init_val = 1.0
        for i in range(len(path) - 1):
            obj = find_detail(path[i], path[i+1])
            # print(obj)
            price = obj['price'] * (1.0 - obj['fee'])
            # print(price)
            init_val *= price
        return init_val
    else:
        print('No available trading pairs')
        return 0


def build_symbol_graph(pairs, fee_dict, price):
    graph = {}
    for key, val in pairs.items():
        asseta = {'base': True, 'fee': float(
            fee_dict[key]['taker']), 'price': float(price[key])}
        assetb = {'base': False, 'fee': float(
            fee_dict[key]['taker']), 'price': 1.0 / float(price[key])}
        if val['baseAsset'] not in graph:
            graph[val['baseAsset']] = {val['quoteAsset']: asseta}
        else:
            graph[val['baseAsset']][val['quoteAsset']] = asseta
        if val['quoteAsset'] not in graph:
            graph[val['quoteAsset']] = {val['baseAsset']: assetb}
        else:
            graph[val['quoteAsset']][val['baseAsset']] = assetb
    return graph


def show_trade_info(trade, realized, gain_val, gain_percent, pairs, baseAsset, quantity):
    time = datetime.fromtimestamp(trade['time'] / 1000, tz=UTC(8))
    symbol = trade["symbol"]
    realize = 'Realized' if realized else 'Unrealized'
    quantity = str(quantity) + " " + baseAsset
    profit = str(gain_val) + " " + baseAsset
    buy_or_sell = 'Buy {}'.format(
        pairs[symbol]['baseAsset'] if trade['isBuyer'] else pairs[symbol]['quoteAsset'])
    print('Trade Time: {}\nTrading Pair: {}\n{} {}\nQuantity: {}\nprice: {}\nprofit: {} / {}%\n'.format(
        time, symbol, buy_or_sell, realize, quantity, trade["price"], profit, gain_percent))


baseAsset = input('Please enter your currency standard (default: USDT):') or 'USDT'
useJson = input('Use JsonTradeHistory? (default: blank):') or ' '
pairs = getAllMarketPairs()
history_trades = getHistoryTrade(pairs, useJson)
history_trades = sorted(
    history_trades, key=lambda x: x['time'])
fee_dict = build_fee_dict(cli.trade_fee())
price_dict = build_price_dict(cli.ticker_price())
graph = build_symbol_graph(pairs, fee_dict, price_dict)
total_gain_val = 0.0
print()
for trade in history_trades:
    symbol = trade['symbol']
    base_asset_rate = show_current_earn(
        graph, pairs[symbol]['baseAsset'], baseAsset)
    quote_asset_rate = show_current_earn(
        graph, pairs[symbol]['quoteAsset'], baseAsset)
    commission_asset_rate = show_current_earn(
        graph, trade["commissionAsset"], baseAsset)

    realized = False
    if trade['isBuyer']:
        before_asset_val = quote_asset_rate * \
            float(trade["quoteQty"]) + \
            commission_asset_rate * float(trade["commission"])
        after_asset_val = base_asset_rate * float(trade["qty"])
        gain_val = after_asset_val - before_asset_val
        gain_percent = gain_val / before_asset_val * 100
        if base_asset_rate == 1.0:
            realized = True
    else:
        before_asset_val = base_asset_rate * float(trade["qty"])
        after_asset_val = quote_asset_rate * float(trade["quoteQty"])
        gain_val = after_asset_val - before_asset_val
        gain_percent = gain_val / before_asset_val * 100
        if quote_asset_rate == 1.0:
            realized = True
    show_trade_info(trade, realized, gain_val, gain_percent, pairs, baseAsset, after_asset_val)
    total_gain_val += gain_val
print('Total gain:', str(total_gain_val) + " " + baseAsset)
