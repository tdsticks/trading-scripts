#!/usr/bin/python3

import sys
try:
    assert sys.version_info >= (3, 0)
except:
    print("Must be ran with Python 3 or greater")
    sys.exit()
import urllib
from urllib.request import urlopen, Request
import time
import json
import decimal
import os


try:
    from api_keys import coinigykey, coinigysec #coinigy api key and secret need to be set in api_keys.py
    import manage_alerts
    from base_scanner_settings import days, skip, minutes, drop, six_candle_up, sensitivity, low_or_close, split_the_difference, delete_old_alerts, exchange, minimum_volume, market
except:
    input("You need to download api_keys.py, put your coinigy keys in it, base_scanner_settings.py, and download manage_alerts.py all from the project site")
    sys.exit()

open("alerts_set.txt", "a")
open("alerts_deleted.txt", "a")
open("alerts_blacklist.txt", "a")
blacklist = open("alerts_blacklist.txt", "r").readlines()
blacklist = [x.upper().strip() for x in blacklist]
# to not set alerts for certain coins, i.e., blacklist them, put the exchange and the coin name in the alerts_blacklisted.txt file with a space in between like this:
####################
# BTRX DOGE BTC
# CPIA LIZI ETH
###################
# and so on but without the pound signs

if len(sys.argv) > 1:
    exchange = sys.argv[1].upper()
    minimum_volume = int(sys.argv[2])
    market = sys.argv[3].upper()

print(days, skip, minutes, drop, six_candle_up, sensitivity, low_or_close, split_the_difference, delete_old_alerts, exchange, minimum_volume, market)

if coinigykey == "---Your-coinigy-key-here---":
    input("You need to put your coinigy key and secret in api_keys.py")
    sys.exit()

headers = {'Content-Type': 'application/json', 'X-API-KEY': coinigykey, 'X-API-SECRET': coinigysec}

#get old alerts
alerts = manage_alerts.AlertManager(coinigykey, coinigysec)
old_alerts = alerts._get_old_alerts()

def get_coins(exch_code):
    l = []
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
    values = '{"exchange_code": "' + exchange_code + '","exchange_market": "' + coin_slash_market  + '"}'
    values = bytes(values, encoding='utf-8')
    request = Request('https://api.coinigy.com/api/v1/ticker', data=values, headers=headers)
    request = urlopen(request).read()
    time.sleep(1)
    request = request.decode("utf-8")
    request = json.loads(request)
    return request


def check_dup_alerts(coin, price):
    for x in old_alerts['data']['open_alerts']:
        if x['mkt_name'] == coin and abs(price - float(x['price'])) < 0.00000001:
            print("Alert already set")
            return True
    return False

def setalert(x, y):
    print("Base at candle " + str(x))
    print("Base price " + str(round(decimal.Decimal(y), 8)))
    print("Alert price " + str(round(decimal.Decimal(y * drop), 8)))
    print("Volume %f" % vol_base)
    #print(min(l))

    #Delete old alerts for this coin
    if delete_old_alerts:
        alerts_deleted = open("alerts_deleted.txt").readlines()
        for line in open("alerts_set.txt"):
            if len(line) > 1 and line.split("\t")[5].strip() == coin + "/" + market and line.split("\t")[4].strip() == exchange and not line in alerts_deleted:
                open("alerts_deleted.txt", "a").write(line)
                notification_id = line.split("\t")[1].strip()
                delete_coins = manage_alerts.AlertManager(coinigykey, coinigysec)
                delete_coins._api_delete_alert(notification_id)
                time.sleep(1)

    values = '{"exch_code": "' + exchange + '", "market_name": "' + coin + '/' + market + '", "alert_price": ' + str(y * drop) + ', "alert_note": ""}'
    values = bytes(values, encoding='utf-8')
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


def sixup(c, x, y):                        
    strikes = 0
    if (x < skip or x > len(c) - 13): return
    l.append(y)
    if (c[x - 1] >= y and
        c[x + 1] >= y and
        c[x - 2] >= y and
        c[x + 2] >= y and
        c[x - 3] > y and
        c[x + 3] > y and
        c[x + 4] > y and
        c[x + 5] > y and
        c[x + 7] > y and
        c[x + 8] > y and
        c[x + 9] > y and
        c[x + 10] > y and
        c[x + 11] > y and
        c[x + 12] > y and
        y <= min(l) and
        (c[x - 6] >= y * six_candle_up or c[x - 7] >= y * six_candle_up) and
        c[x - 6] - y > 0.00000002 and #To eliminate false positives for low sat coins like DOGE and RDD
        (c[x + 6] >= y * six_candle_up or c[x + 7] >= y * six_candle_up) and
        c[x + 6] - y > 0.00000002
        ):
            if c[x - 3] < c[x - 1]: strikes += 1
            if c[x - 4] < c[x - 2]: strikes += 1
            if c[x - 5] < c[x - 3]: strikes += 1
            if c[x + 3] < c[x + 1]: strikes += 1
            if c[x + 4] < c[x + 2]: strikes += 1
            if c[x + 5] < c[x + 3]: strikes += 1
            print(str(strikes) + " strike(s) against potential base at candle " + str(x))
            if strikes <= sensitivity:
                dupe = check_dup_alerts(coin + "/" + market, y * drop)
                if dupe:
                    return "nextcoin"
                if not dupe and last_price > y * drop:
                    setalert(x, y)
                    return "nextcoin"

def avgthree(c, x, y):
    #print(x)
    #print(y)
    strikes = 0
    if (x < skip or x > len(c) - (13)): return
    l.append(y)
    if (c[x - 1] >= y and
        c[x + 1] >= y and
        c[x - 2] >= y and
        c[x + 2] >= y and
        c[x - 3] > y and
        c[x + 3] > y and
        c[x - 4] > y and
        c[x + 4] > y and
        c[x - 5] > y and
        c[x + 5] > y and
        c[x + 7] > y and
        c[x + 8] > y and
        c[x + 9] > y and
        c[x + 10] > y and
        c[x + 11] > y and
        c[x + 12] > y and
        y <= min(l) and
        c[x - 6] >= y * six_candle_up and
        c[x - 6] - y > 0.00000002 and #To eliminate false positives for low sat coins like DOGE and RDD
        c[x + 6] >= y * six_candle_up and
        c[x + 6] - y > 0.00000002 and
        (c[x - 1] + c[x - 2] + c[x - 3]) / 3 < (c[x - 2] + c[x - 3] + c[x - 4]) / 3 < (c[x - 4] + c[x - 5] + c[x - 6]) / 3 and
        (c[x + 1] + c[x + 2] + c[x + 3]) / 3 < (c[x + 2] + c[x + 3] + c[x + 4]) / 3 < (c[x + 4] + c[x + 5] + c[x + 6]) / 3
        ):
            print(str(strikes) + " strike(s) against potential base at candle " + str(x))
            if strikes <= sensitivity:
                dupe = check_dup_alerts(coin + "/" + market, y * drop)
                if dupe:
                    return "nextcoin"
                if not dupe and last_price > y * drop:
                    setalert(x, y)
                    return "nextcoin"

def blacklisted(exchange, coin, market, blacklist):
    for x in blacklist:
        if x.split()[0] == exchange and x.split()[1] == coin and x.split()[2] == market:
            return True


if __name__ == "__main__":
    coins = get_coins(exchange)
    for coin in coins:
        if len(blacklist) > 0 and blacklisted(exchange, coin, market, blacklist) == True:
            print("\n", exchange, coin, "blacklisted")
            continue 
        #coin = "DYN"
        print("\n" + exchange + " " + market + " " + coin + " scanning")
        #input("Press enter to continue")
        vol_base = get_coin_price_volume(exchange, coin + '/' + market)
        try:
            last_price = float(vol_base['data'][0]['last_trade'])
            vol_base = float(vol_base['data'][0]['current_volume']) * float(vol_base['data'][0]['last_trade'])
        except:
            print(vol_base)
            continue
        if vol_base < minimum_volume:
            continue
        print(str(vol_base) + " volume")

        while True:
            try:
                candles = urlopen("https://www.coinigy.com/getjson/chart_feed/" + 
                             exchange + "/" + 
                             coin + "/" + 
                             market + "/" + 
                             minutes + "/" + 
                             str(round(time.time()-(int(86400 * days)))) + "/" + 
                             str(round(time.time()))).read().decode("utf-8"
                            )
            except Exception as e:
                print(e)
                print("Will try again in 10 seconds")
                time.sleep(10)
            else:
                break
                

        time.sleep(2)
        candles = json.loads(candles)

        if split_the_difference:
            candles = [(float(x[3]) + float(x[4])) / 2 for x in candles]
        else:
            candles = [float(x[low_or_close]) for x in candles]


        l = []


        for x, y in enumerate(candles):
            if sixup(candles, x, y) == "nextcoin":
                print("sixup")
                break
            if avgthree(candles, x, y) == "nextcoin":
                print("avgthree")
                break
