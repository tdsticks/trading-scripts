#!/usr/bin/python3

import urllib
from urllib.request import urlopen, Request
import time
import json
import decimal
import os
import time
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
days = 14 #how far back to look for bases. Suggested at least 14 for base breaks and 1 for day trading
skip = 6 #this is how many candles back from now we ignore when scanning for bases; has to be at least 6
market = "BTC"
exchange = "BTRX"
minutes = "60" #candle time interval. suggested 60 for regular base breaks, 3 for day trading
drop = .96 #percentage below detected bases to set alert so .96 is 4% down. Suggest at least .96 or .95 for regular base breaks and .97 for day trading
six_candle_up = 1.05 #how much higher the sixth candles from the base should be relative to the base. Suggested at least 1.05 for 1 hour and 1.03 for 3 minute day trading candles
sensitivity = 2 #A number 0-6 for how sensitive the scanner is to quality bases. Lower number allows higher quality bases but less of them. 1 or 2 seems to work best
low_or_close = 3 #whether you want bases based on the low or the close (bottom of wick or candle respectively). 3 gives you low and 4 is close. (Also 0 is open and 1 is high if you want to go there)
split_the_difference = False #Detects bases at 50% of wicks rather than the low or close prices. Setting this to True will cause the low_or_close variable to be ignored
minimum_volume = 10 #Filters out all coins whose volume (in BTC in the last 24h) is less than this amount
###############VARIABLES TO SET


if coinigykey == "---Your-coinigy-key-here---":
    input("You need to put your coinigy key and secret in api_keys.py")
    sys.exit()

summaries = urlopen("https://bittrex.com/api/v1.1/public/getmarketsummaries").read().decode("utf-8")
summaries = json.loads(summaries)

#get old alerts
alerts = z_manage_alerts.AlertManager(coinigykey, coinigysec)
old_alerts = alerts._get_old_alerts()

def check_dup_alerts(coin, price):
    for x in old_alerts['data']['open_alerts']:
        if x['mkt_name'] == coin and abs(price - float(x['price'])) < 0.00000001:
            print("Alert already set")
            return True
    return False



for coin in summaries['result']:
    vol_base = coin['BaseVolume']
    coin = coin['MarketName']
    if not market in coin or 'USDT' in coin or vol_base < minimum_volume:
        continue
    coin = coin.split('-')[1]
    #coin = "ABY"
    print(coin)

    a = urlopen("https://www.coinigy.com/getjson/chart_feed/" + 
                 exchange + "/" + 
                 coin + "/" + 
                 market + "/" + 
                 minutes + "/" + 
                 str(round(time.time()-(86400 * days))) + "/" + 
                 str(round(time.time()))).read().decode("utf-8"
                 )

    time.sleep(1)
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
                    #print(min(l))
                    values = '{"exch_code": "BTRX", "market_name": "' + coin + '/' + market + '", "alert_price": ' + str(y * drop) + ', "alert_note": ""}'
                    values = bytes(values, encoding='utf-8')
                    headers = {'Content-Type': 'application/json','X-API-KEY': coinigykey, 'X-API-SECRET': coinigysec}
                    request = Request('https://api.coinigy.com/api/v1/addAlert', data=values, headers=headers)
                    response_body = urlopen(request).read()
                    time.sleep(1)
                    print(response_body)
                    response_body = response_body.decode("utf-8")
                    response_body = json.loads(response_body)
                    new_alert = alerts._get_old_alerts()['data']['open_alerts'][-1]
                    time.sleep(1)
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
input("FINISHED")
