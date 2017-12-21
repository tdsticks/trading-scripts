#!/usr/bin/python3

import decimal
import json
import sys
import time
from urllib.request import urlopen, Request

import manage_alerts
from util import verify_python3_or_exit
from base_scanner_settings import settings
import api_keys
from coinigy import CoinigyToken

verify_python3_or_exit()


# TODO: move downward
def _prepare_coinigy_token():
    if api_keys.coinigykey == "---Your-coinigy-key-here---":
        input("You need to put your coinigy key and secret in api_keys.py")
        sys.exit()

    return CoinigyToken(token=api_keys.coinigykey, secret=api_keys.coinigysec)


coinigy_token = _prepare_coinigy_token()

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
    settings.days = int(sys.argv[1])
    settings.skip = int(sys.argv[2])
    settings.minutes = int(str(sys.argv[3]))
    settings.drop = float(sys.argv[4])
    settings.six_candle_up = float(sys.argv[5])
    settings.sensitivity = int(sys.argv[6])
    settings.low_or_close = int(sys.argv[7])
    settings.split_the_difference = sys.argv[8]
    settings.delete_old_alerts = sys.argv[9]
    settings.exchange = sys.argv[10].upper()
    settings.minimum_volume = int(sys.argv[11])
    settings.market = sys.argv[12].upper()

if settings.split_the_difference == "False":
    settings.split_the_difference = False
if settings.delete_old_alerts == "False":
    settings.delete_old_alerts = False

print(settings.days, settings.skip, settings.minutes, settings.drop, settings.six_candle_up, settings.sensitivity,
      settings.low_or_close, settings.split_the_difference, settings.delete_old_alerts,
      settings.exchange, settings.minimum_volume, settings.market)

headers = {'Content-Type': 'application/json', 'X-API-KEY': coinigy_token.token, 'X-API-SECRET': coinigy_token.secret}

# get old alerts
alerts = manage_alerts.AlertManager(coinigy_token)
old_alerts = alerts._get_old_alerts()


def get_coins(exch_code):
    l = []
    values = '{"exch_code": ' + settings.exchange + '}'
    values = bytes(values, encoding='utf-8')
    request = Request('https://api.coinigy.com/api/v1/markets', data=values, headers=headers)
    coin_list = urlopen(request).read()
    time.sleep(1)
    coin_list = coin_list.decode("utf-8")
    coin_list = json.loads(coin_list)
    for x in coin_list['data']:
        if x['exch_code'] == exch_code:
            l.append(x['mkt_name'])
    l = [x.split('/')[0] for x in l if x.split('/')[1] == settings.market]
    return l


def get_coin_price_volume(exchange_code, coin_slash_market):
    values = '{"exchange_code": "' + exchange_code + '","exchange_market": "' + coin_slash_market + '"}'
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
    print("Alert price " + str(round(decimal.Decimal(y * settings.drop), 8)))
    print("Volume %f" % vol_base)
    # print(min(l))

    # Delete old alerts for this coin
    if settings.delete_old_alerts:
        alerts_deleted = open("alerts_deleted.txt").readlines()
        for line in open("alerts_set.txt"):
            if len(line) > 1 and line.split("\t")[5].strip() == coin + "/" + settings.market and line.split("\t")[
                4].strip() == settings.exchange and not line in alerts_deleted:
                open("alerts_deleted.txt", "a").write(line)
                notification_id = line.split("\t")[1].strip()
                delete_coins = manage_alerts.AlertManager(coinigy_token)
                delete_coins._api_delete_alert(notification_id)
                time.sleep(1)

    values = '{"exch_code": "' + settings.exchange + '", "market_name": "' + coin + '/' + settings.market + '", "alert_price": ' + str(
        y * settings.drop) + ', "alert_note": ""}'
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
    if new_alert['mkt_name'] == coin + '/' + settings.market:
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
    if (x < settings.skip or x > len(c) - 13): return
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
            (c[x - 6] >= y * settings.six_candle_up or c[x - 7] >= y * settings.six_candle_up) and
            c[x - 6] - y > 0.00000002 and  # To eliminate false positives for low sat coins like DOGE and RDD
            (c[x + 6] >= y * settings.six_candle_up or c[x + 7] >= y * settings.six_candle_up) and
            c[x + 6] - y > 0.00000002
    ):
        if c[x - 3] < c[x - 1]: strikes += 1
        if c[x - 4] < c[x - 2]: strikes += 1
        if c[x - 5] < c[x - 3]: strikes += 1
        if c[x + 3] < c[x + 1]: strikes += 1
        if c[x + 4] < c[x + 2]: strikes += 1
        if c[x + 5] < c[x + 3]: strikes += 1
        print(str(strikes) + " strike(s) against potential base at candle " + str(x))
        if strikes <= settings.sensitivity:
            dupe = check_dup_alerts(coin + "/" + settings.market, y * settings.drop)
            if dupe:
                return "nextcoin"
            if not dupe and last_price > y * settings.drop:
                setalert(x, y)
                return "nextcoin"


def avgthree(c, x, y):
    # print(x)
    # print(y)
    strikes = 0
    if (x < settings.skip or x > len(c) - (13)): return
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
            c[x - 6] >= y * settings.six_candle_up and
            c[x - 6] - y > 0.00000002 and  # To eliminate false positives for low sat coins like DOGE and RDD
            c[x + 6] >= y * settings.six_candle_up and
            c[x + 6] - y > 0.00000002 and
            (c[x - 1] + c[x - 2] + c[x - 3]) / 3 < (c[x - 2] + c[x - 3] + c[x - 4]) / 3 < (
                    c[x - 4] + c[x - 5] + c[x - 6]) / 3 and
            (c[x + 1] + c[x + 2] + c[x + 3]) / 3 < (c[x + 2] + c[x + 3] + c[x + 4]) / 3 < (
                    c[x + 4] + c[x + 5] + c[x + 6]) / 3
    ):
        print(str(strikes) + " strike(s) against potential base at candle " + str(x))
        if strikes <= settings.sensitivity:
            dupe = check_dup_alerts(coin + "/" + settings.market, y * settings.drop)
            if dupe:
                return "nextcoin"
            if not dupe and last_price > y * settings.drop:
                setalert(x, y)
                return "nextcoin"


def blacklisted(exchange, coin, market, blacklist):
    for x in blacklist:
        if x.split()[0] == exchange and x.split()[1] == coin and x.split()[2] == market:
            return True


if __name__ == "__main__":
    coins = get_coins(settings.exchange)
    for coin in coins:
        if len(blacklist) > 0 and blacklisted(settings.exchange, coin, settings.market, blacklist) == True:
            print("\n", settings.exchange, coin, "blacklisted")
            continue
            # coin = "DYN"
        print("\n" + settings.exchange + " " + settings.market + " " + coin + " scanning")
        # input("Press enter to continue")
        vol_base = get_coin_price_volume(settings.exchange, coin + '/' + settings.market)
        try:
            last_price = float(vol_base['data'][0]['last_trade'])
            vol_base = float(vol_base['data'][0]['current_volume']) * float(vol_base['data'][0]['last_trade'])
        except:
            print(vol_base)
            continue
        if vol_base < settings.minimum_volume:
            continue
        print(str(vol_base) + " volume")

        while True:
            try:
                candles = urlopen("https://www.coinigy.com/getjson/chart_feed/" +
                                  settings.exchange + "/" +
                                  coin + "/" +
                                  settings.market + "/" +
                                  str(settings.minutes) + "/" +
                                  str(round(time.time() - (int(86400 * settings.days)))) + "/" +
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

        if settings.split_the_difference:
            candles = [(float(x[3]) + float(x[4])) / 2 for x in candles]
        else:
            candles = [float(x[settings.low_or_close]) for x in candles]

        l = []

        for x, y in enumerate(candles):
            if sixup(candles, x, y) == "nextcoin":
                print("sixup")
                break
            if avgthree(candles, x, y) == "nextcoin":
                print("avgthree")
                break
