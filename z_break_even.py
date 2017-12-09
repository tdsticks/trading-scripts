#!/usr/bin/python3

import sys
import decimal
from urllib.request import urlopen
import json
try:
    import bittrex
except:
    print("You need the bittrex.py api python wrapper from: https://github.com/ericsomdahl/python-bittrex/blob/master/bittrex/bittrex.py")


####Put your key and secret here
api_key='--your-bittrex-api-key-here--'
api_secret='--your-bittrex-api-secret-here--'
####


if api_key == '--your-bittrex-api-key-here--':
    print("You need your bittrex api key and secret in the file")
    print("It just needs to be able to read your account balance and transaction history for the coin in question.\nMake sure you don't enable withdrawal permissions")
    sys.exit()

b = bittrex.Bittrex(api_key, api_secret)

try:
    symbol = sys.argv[1]
    market = symbol.split("-")[0]
except:
    print("""Must be market then coin. 
Example: 
$ break_even.py BTC-NEO
This will give you results for the BTC-NEO trading pair""")
    sys.exit()

balance = round(b.get_balance(symbol.split("-")[1])['result']['Balance'], 8)
print(str(balance) + " balance")

howfarback = 1000 #this is how many transactions to attempt to get for the coin. Default is an arbitrarily large number
res = b.get_order_history(symbol, howfarback)
res = res['result']

l = []
m = []

#one way to calculate how far back is to get the current balance and see how many buys and sells back we have to go to get that quantity
for x in res:
    if x['OrderType'] == 'LIMIT_SELL':
        l.append(round(x['Price'] - x['Commission'], 8))
        m.append((x['Quantity'] - x['QuantityRemaining']) * -1)
    else:
        l.append(round((x['Price'] + x['Commission']) * -1, 8))
        m.append(x['Quantity'] - x['QuantityRemaining'])
    #print(sum(m))
    if abs(sum(m) - balance) / balance < 0.005: #float accuracy issues necessitate this
        d = x['Closed']
        break
else:
    print("\n#################")
    print("Transactions aren't adding up to your balance")
    print("Costs")
    print(l)
    print("Quantities")
    print(m)
    sys.exit()

print("Transactions COST/PROCEEDS:")
print(l)
print("Last relevant transaction dated: " + d + " UTC")
#print(m)



pl = round(sum(l), 8)
print(str(pl) + " net cost in " + market + " for these transactions")


exrate = dict(json.loads(str(urlopen("https://bittrex.com/api/v1.1/public/getticker?market=USDT-" + market).read().decode())))['result']['Last']
print(str(round(pl * exrate, 2)) + " net cost in USD for these transactions at the current market rate of " + str(exrate) + " USDT per " + market)


if pl < 0 and balance > 0:
    print("Sell at:")

    sellfor = (abs(pl) / balance) * 1.00255 #the extra 0.00005 seems to be needed for accuracy
    sellfor = round(sellfor, 8)
    print(str(decimal.Decimal(str(sellfor))) + " to break even")
    for x in [1.01, 1.02, 1.03, 1.04, 1.05]:
        print(str(decimal.Decimal(str(round(sellfor * x, 8)))) + " for " + str(x) + "%")
