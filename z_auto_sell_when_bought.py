#!/usr/bin/python3
#public domain

#Works with bitcoin since that's all I trade. Takes a symbol like NEO as the first argument and a rate like 0.014324823 as the second argument. It checks every so often
#and when it sees you have a quantity of that coin like say when a buy is triggered, it puts it up for sale at that price.
#for example: auto_sell.py ETH 0.014324823
#simple as that

import bittrex
import sys
import time
import decimal

try:
    sys.argv[2]
except:
    print("Must have symbol then rate")
    sys.exit()

api_key='---YOUR-KEY-HERE---'
api_secret='---YOUR-SECRET-HERE---'

b = bittrex.Bittrex(api_key, api_secret)
symbol = sys.argv[1]
rate = sys.argv[2]


while True:
    try:
        quant = b.get_balance(symbol)['result']['Available']
        print("Available: " + str(quant) + " " + symbol)
        if quant > 0:
            sell = b.sell_limit("BTC-" + symbol, quant, rate)
            print(sell)
    except Exception as e:
        print(e)
    time.sleep(122)
