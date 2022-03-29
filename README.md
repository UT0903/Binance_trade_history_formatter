# Binance_trade_history_formatter

## Introduction
* Implemented by binance API (python binance-connector).
* Can calculate profit for each history trade.
* Use BFS to find the least trading times.
* Profit is calculate by current price, and include taker fee.
* Can show trade info by different currency standards.
* Future work: Can find the cheapest path for two coins

![pic1](https://user-images.githubusercontent.com/48646032/160671276-70b424a8-9c38-4a84-ac6c-248738ce3fb4.png)

## How to Use

0. How to create Binance API key: https://www.binance.com/en/support/faq/c-6

1. Create a file named **'secret.py'**, and add the following in the file, remember to change to your own api key and secret.

```
// secret.py
my_api_key = 'YOUR_API_KEY'
my_api_secret = 'YOUR_API_SECRET'
```

2. Install pip requirement in requirement.txt

```
pip3 install -r requirement.txt
```

3. Now you can run the code
```
python3 my_trade.py
```

4. Sample Output

![demo1](https://user-images.githubusercontent.com/48646032/160670893-571fb51c-df87-4433-b272-1db475a0de2c.png)

![demo2](https://user-images.githubusercontent.com/48646032/160670906-17b9bb97-da21-49f6-8f9a-ab504fd7d5ae.png)
