#!/usr/bin/python3

import urllib
from urllib.request import urlopen, Request
import time
import json
import decimal
import os
import sys
try:
    from api_keys import coinigykey, coinigysec #coinigy api key and secret need to be set in api_keys.py
    import z_manage_alerts
except:
    input("You need to download api_keys.py, put your coinigy keys in it, and download z_manage_alerts.py all from the project site")
    sys.exit()

##################################################################################################
#########################     PYTHON 3 is a must Python 2 will not work     ######################
##################################################################################################

##############VARIABLES TO SET
days = 60 #how far back to look for bases. Suggested at least 14 for base breaks and 1 for day trading
skip = 6 #this is how many candles back from now we ignore when scanning for bases; has to be at least 6
market = "BTC" #Market like BTC or ETH
minutes = "60" #candle time interval. suggested 60 for regular base breaks, 3 for day trading
drop = .96 #percentage below detected bases to set alert so .96 is 4% down. Suggest at least .96 or .95 for regular base breaks and .97 for day trading
six_candle_up = 1.05 #how much higher the sixth candles from the base should be relative to the base. Suggested at least 1.05 for 1 hour and 1.03 for 3 minute day trading candles
sensitivity = 2 #A number 0-6 for how sensitive the scanner is to quality bases. Lower number allows higher quality bases but less of them. 1 or 2 seems to work best
low_or_close = 3 #whether you want bases based on the low or the close (bottom of wick or candle respectively). 3 gives you low and 4 is close. (Also 0 is open and 1 is high if you want to go there)
split_the_difference = False #Detects bases at 50% of wicks rather than the low or close prices. Setting this to True will cause the low_or_close variable to be ignored
if len(sys.argv) > 1:
    exchange = sys.argv[1]
    minimum_volume = int(sys.argv[2])
else:
    exchange = "BTRX"
    minimum_volume = 10 #Filters out all coins whose volume (in base coin in the last 24h) is less than this amount
###############VARIABLES TO SET


if coinigykey == "---Your-coinigy-key-here---":
    input("You need to put your coinigy key and secret in api_keys.py")
    sys.exit()


def get_coins(exch_code):
    l = []
    headers = {'Content-Type': 'application/json', 'X-API-KEY': coinigykey, 'X-API-SECRET': coinigysec}
    values = '{"exch_code": ' + exchange + '}'
    values = bytes(values, encoding='utf-8')
    request = Request('https://api.coinigy.com/api/v1/markets', data=values, headers=headers)
    coin_list = urlopen(request).read()
    time.sleep(1)
    coin_list = coin_list.decode("utf-8")
    coin_list = json.loads(coin_list)
    for x in coin_list['data']:
        if x['exch_code'] == exch_code:
           l.append(x['mkt_name'])
    l = [x.split('/')[0] for x in l if x.split('/')[1] == market]
    return l

def get_coin_price_volume(exchange_code, coin_slash_market):
    headers = {'Content-Type': 'application/json', 'X-API-KEY': coinigykey, 'X-API-SECRET': coinigysec}
    values = '{"exchange_code": "' + exchange_code + '","exchange_market": "' + coin_slash_market  + '"}'
    values = bytes(values, encoding='utf-8')
    request = Request('https://api.coinigy.com/api/v1/ticker', data=values, headers=headers)
    request = urlopen(request).read()
    time.sleep(1)
    request = request.decode("utf-8")
    request = json.loads(request)
    return request

#get old alerts
alerts = z_manage_alerts.AlertManager(coinigykey, coinigysec)
old_alerts = alerts._get_old_alerts()

def check_dup_alerts(coin, price):
    for x in old_alerts['data']['open_alerts']:
        if x['mkt_name'] == coin and abs(price - float(x['price'])) < 0.00000001:
            print("Alert already set")
            return True
    return False


coins = get_coins(exchange)
for coin in coins:
    print(coin)
    vol_base = get_coin_price_volume(exchange, coin + '/' + market)
    try:
        vol_base = float(vol_base['data'][0]['current_volume']) * float(vol_base['data'][0]['last_trade'])
    except:
        print(vol_base)
        continue
    if vol_base < minimum_volume:
        continue

    a = urlopen("https://www.coinigy.com/getjson/chart_feed/" + 
                 exchange + "/" + 
                 coin + "/" + 
                 market + "/" + 
                 minutes + "/" + 
                 str(round(time.time()-(86400 * days))) + "/" + 
                 str(round(time.time()))).read().decode("utf-8"
                 )

    time.sleep(2)
    b = json.loads(a)

    c = [x[low_or_close] for x in b]
    if split_the_difference:
        c = [str((float(x[3]) + float(x[4])) / 2) for x in b]
    c = [float(x) for x in c]

    l = []

    strikes = 0
    for x, y in enumerate(c):
        if (x < skip or x > len(c) - (skip + 1)): continue
        l.append(y)
        if (c[x - 1] >= y and
            c[x + 1] >= y and
            c[x - 2] >= y and
            c[x + 2] >= y and
            y <= min(l) and
            c[x - 6] >= y * six_candle_up and
            c[x + 6] >= y * six_candle_up
            ):
                if c[x - 3] < c[x - 1]: strikes += 1
                if c[x - 4] < c[x - 2]: strikes += 1
                if c[x - 5] < c[x - 3]: strikes += 1
                if c[x + 3] < c[x + 1]: strikes += 1
                if c[x + 4] < c[x + 2]: strikes += 1
                if c[x + 5] < c[x + 3]: strikes += 1
                if strikes <= sensitivity and not check_dup_alerts(coin + "/" + market, y * drop):
                    print(str(strikes) + " strike(s) against this base")
                    print("Base at candle " + str(x))
                    print("Base price " + str(round(decimal.Decimal(y), 8)))
                    print("Alert price " + str(round(decimal.Decimal(y * drop), 8)))
                    print("Volume %f" % vol_base)
                    #print(min(l))
                    values = '{"exch_code": "' + exchange + '", "market_name": "' + coin + '/' + market + '", "alert_price": ' + str(y * drop) + ', "alert_note": ""}'
                    values = bytes(values, encoding='utf-8')
                    headers = {'Content-Type': 'application/json','X-API-KEY': coinigykey, 'X-API-SECRET': coinigysec}
                    request = Request('https://api.coinigy.com/api/v1/addAlert', data=values, headers=headers)
                    response_body = urlopen(request).read()
                    time.sleep(2)
                    print(response_body)
                    response_body = response_body.decode("utf-8")
                    response_body = json.loads(response_body)
                    new_alert = alerts._get_old_alerts()['data']['open_alerts'][-1]
                    time.sleep(2)
                    print(new_alert)
                    if new_alert['mkt_name'] == coin + '/' + market:
                        open("alerts_set.txt", "a").write(
                                                          str(time.time()) + "\t" + 
                                                          new_alert["alert_id"] + "\t" + 
                                                          new_alert["alert_added"] + "\t" +
                                                          new_alert["price"] + "\t" +
                                                          new_alert["exch_code"] + "\t" +
                                                          new_alert["mkt_name"] + "\n"
                                                      )
                    break
#input("FINISHED")
