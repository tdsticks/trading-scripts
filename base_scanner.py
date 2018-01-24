#!/usr/bin/python3

import decimal
import json
import sys
import time
from argparse import ArgumentParser
from urllib.request import urlopen, Request

import api_keys
from base_scanner_settings import user_settings as settings_from_file
from coinigy import CoinigyToken
from manage_alerts import AlertManager
from util import verify_python3_or_exit


# TODO: extract to a different module
class Scanner:
    def __init__(self, settings, coinigy_token, alerts, blacklist=None):
        self._settings = settings
        self._coinigy_token = coinigy_token
        self._alerts = alerts
        self._blacklist = blacklist if blacklist else []
        self._headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self._coinigy_token.token,
            'X-API-SECRET': self._coinigy_token.secret
        }
        self._old_alerts = self._alerts.get_old_alerts()

    def get_coins(self, exch_code):
        l = []
        cl = [] # Coin List

        values = '{"exch_code": ' + self._settings.exchange + '}'
        values = bytes(values, encoding='utf-8')

        request = Request('https://api.coinigy.com/api/v1/markets', data=values, headers=self._headers)

        coin_list = urlopen(request).read()
        time.sleep(1)
        coin_list = coin_list.decode("utf-8")
        coin_list = json.loads(coin_list)

        for x in coin_list['data']:
            if x['exch_code'] == exch_code:
                l.append(x['mkt_name'])

        for coin in l:
            c = coin.split('/')[0]
            mkt = coin.split('/')[1]
            # print(c,mkt)

            if mkt in self._settings.market:
                # print(c, mkt)
                cl.append(c)
        # print("coin list:", cl)

        return cl

    def get_coin_price_volume(self, exchange_code, coin_slash_market):
        values = '{"exchange_code": "' + exchange_code + '","exchange_market": "' + coin_slash_market + '"}'
        values = bytes(values, encoding='utf-8')
        request = Request('https://api.coinigy.com/api/v1/ticker', data=values, headers=self._headers)
        request = urlopen(request).read()
        time.sleep(1)
        request = request.decode("utf-8")
        request = json.loads(request)
        return request

    def check_dup_alerts(self, coin, price):
        for x in self._old_alerts['data']['open_alerts']:
            if x['mkt_name'] == coin and abs(price - float(x['price'])) < 0.00000001:
                print("Alert already set")
                return True
        return False

    def setalert(self, x, y, coin, vol_base, mkt):
        print("Base at candle " + str(x))
        print("Base price " + str(round(decimal.Decimal(y), 8)))
        print("Alert price " + str(round(decimal.Decimal(y * self._settings.drop), 8)))
        print("Volume %f" % vol_base)
        # print(min(l))

        # Delete old alerts for this coin
        if self._settings.delete_old_alerts:
            alerts_deleted = open("alerts_deleted.txt").readlines()
            for line in open("alerts_set.txt"):
                if len(line) > 1 and line.split("\t")[5].strip() == coin + "/" + mkt and \
                        line.split("\t")[
                            4].strip() == self._settings.exchange and line not in alerts_deleted:
                    open("alerts_deleted.txt", "a").write(line)
                    notification_id = line.split("\t")[1].strip()
                    delete_coins = AlertManager(self._coinigy_token)
                    delete_coins._api_delete_alert(notification_id)
                    time.sleep(1)

        #
        # TODO: alert_note still doesn't work with the API for some reason, still need to find out why
        #
        alert_note = "%s %i%%" % ("drop", (100 - float(settings_from_file['drop'][0]) * 100))
        # print("alert_note", alert_note)

        values = '{"exch_code": "' + self._settings.exchange + '", "market_name": "' + coin + '/' + mkt+ \
                 '", "alert_price": ' + str(y * self._settings.drop) + ', "alert_note": "'+alert_note+'"}'

        values = bytes(values, encoding='utf-8')
        request = Request('https://api.coinigy.com/api/v1/addAlert', data=values, headers=self._headers)
        response_body = urlopen(request).read()
        time.sleep(2)
        print(response_body)
        response_body = response_body.decode("utf-8")
        response_body = json.loads(response_body)
        new_alert = self._alerts.get_old_alerts()['data']['open_alerts'][-1]
        time.sleep(2)
        print(new_alert)
        if new_alert['mkt_name'] == coin + '/' + mkt:
            open("alerts_set.txt", "a").write(
                str(time.time()) + "\t" +
                new_alert["alert_id"] + "\t" +
                new_alert["alert_added"] + "\t" +
                new_alert["price"] + "\t" +
                new_alert["exch_code"] + "\t" +
                new_alert["mkt_name"] + "\n"
            )

    def sixup(self, c, x, y, l, coin, vol_base, last_price, mkt):
        strikes = 0
        if (x < self._settings.skip or x > len(c) - 13): return
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
                (c[x - 6] >= y * self._settings.six_candle_up or c[x - 7] >= y * self._settings.six_candle_up) and
                c[x - 6] - y > 0.00000002 and  # To eliminate false positives for low sat coins like DOGE and RDD
                (c[x + 6] >= y * self._settings.six_candle_up or c[x + 7] >= y * self._settings.six_candle_up) and
                c[x + 6] - y > 0.00000002
        ):
            if c[x - 3] < c[x - 1]: strikes += 1
            if c[x - 4] < c[x - 2]: strikes += 1
            if c[x - 5] < c[x - 3]: strikes += 1
            if c[x + 3] < c[x + 1]: strikes += 1
            if c[x + 4] < c[x + 2]: strikes += 1
            if c[x + 5] < c[x + 3]: strikes += 1
            print(str(strikes) + " strike(s) against potential base at candle " + str(x))
            if strikes <= self._settings.sensitivity:
                dupe = self.check_dup_alerts(coin + "/" + mkt, y * self._settings.drop)
                if dupe:
                    return "nextcoin"
                if not dupe and last_price > y * self._settings.drop:
                    self.setalert(x, y, coin, vol_base, mkt)
                    return "nextcoin"

    def avgthree(self, c, x, y, l, coin, vol_base, last_price, mkt):
        # print(x)
        # print(y)
        strikes = 0
        if (x < self._settings.skip or x > len(c) - (13)): return
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
                c[x - 6] >= y * self._settings.six_candle_up and
                c[x - 6] - y > 0.00000002 and  # To eliminate false positives for low sat coins like DOGE and RDD
                c[x + 6] >= y * self._settings.six_candle_up and
                c[x + 6] - y > 0.00000002 and
                (c[x - 1] + c[x - 2] + c[x - 3]) / 3 < (c[x - 2] + c[x - 3] + c[x - 4]) / 3 < (
                        c[x - 4] + c[x - 5] + c[x - 6]) / 3 and
                (c[x + 1] + c[x + 2] + c[x + 3]) / 3 < (c[x + 2] + c[x + 3] + c[x + 4]) / 3 < (
                        c[x + 4] + c[x + 5] + c[x + 6]) / 3
        ):
            print(str(strikes) + " strike(s) against potential base at candle " + str(x))
            if strikes <= self._settings.sensitivity:
                dupe = self.check_dup_alerts(coin + "/" + mkt, y * self._settings.drop)
                if dupe:
                    return "nextcoin"
                if not dupe and last_price > y * self._settings.drop:
                    self.setalert(x, y, coin, vol_base, mkt)
                    return "nextcoin"

    def _is_blacklisted(self, exchange, coin, market):
        for x in self._blacklist:
            if x.split()[0] == exchange and x.split()[1] == coin and x.split()[2] == market:
                return True

    def scan_for_bases_and_set_alerts(self):
        coins = self.get_coins(self._settings.exchange)
        # print("coins",coins)

        for coin in coins:

            for mkt in self._settings.market:
                # print("mkt", mkt, "coin", coin)

                if self._blacklist and self._is_blacklisted(self._settings.exchange, coin, mkt):
                    print("\n", self._settings.exchange, coin, "blacklisted")
                    continue
                    # coin = "DYN"
                print("\n" + self._settings.exchange + " " + mkt + " " + coin + " scanning")


                # input("Press enter to continue")
                vol_base = self.get_coin_price_volume(self._settings.exchange, coin + '/' + mkt)
                try:
                    last_price = float(vol_base['data'][0]['last_trade'])
                    vol_base = float(vol_base['data'][0]['current_volume']) * float(vol_base['data'][0]['last_trade'])
                except:
                    print(vol_base)
                    continue
                if vol_base < self._settings.minimum_volume:
                    continue
                print(str(vol_base) + " volume")

                while True:
                    try:
                        candles = urlopen("https://www.coinigy.com/getjson/chart_feed/" +
                                          self._settings.exchange + "/" +
                                          coin + "/" +
                                          mkt + "/" +
                                          str(self._settings.minutes) + "/" +
                                          str(round(time.time() - (int(86400 * self._settings.days)))) + "/" +
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

                if self._settings.split_the_difference:
                    candles = [(float(x[3]) + float(x[4])) / 2 for x in candles]
                else:
                    candles = [float(x[self._settings.low_or_close]) for x in candles]

                l = []

                for x, y in enumerate(candles):
                    if self.sixup(candles, x, y, l, coin, vol_base, last_price, mkt) == "nextcoin":
                        print("sixup")
                        break
                    if self.avgthree(candles, x, y, l, coin, vol_base, last_price, mkt) == "nextcoin":
                        print("avgthree")
                        break


def main():
    verify_python3_or_exit()
    coinigy_token = _prepare_coinigy_token()
    settings = _prepare_settings_from_command_line_and_file(settings_from_file)
    _initialize_alert_files()

    scanner = Scanner(settings, coinigy_token, AlertManager(coinigy_token), _prepare_blacklist())
    scanner.scan_for_bases_and_set_alerts()


def _initialize_alert_files():
    # TODO: open the files in a single place and create them only if required
    for filename in ["alerts_set.txt", "alerts_deleted.txt", "alerts_blacklist.txt"]:
        with open(filename, "a") as _:
            pass


def _prepare_coinigy_token():
    if api_keys.coinigykey == "---Your-coinigy-key-here---":
        input("You need to put your coinigy key and secret in api_keys.py")
        sys.exit()

    return CoinigyToken(token=api_keys.coinigykey, secret=api_keys.coinigysec)


def _prepare_settings_from_command_line_and_file(params_from_file):
    parser = ArgumentParser()
    for param_name in params_from_file:
        param = params_from_file[param_name]
        parser.add_argument("--{}".format(param_name), type=type(param.value), default=param.value, help=param.help)

    parsed_settings = parser.parse_args()
    print("Settings:\n", parsed_settings)

    return parsed_settings


def _prepare_blacklist():
    # to not set alerts for certain coins, i.e., blacklist them, put the exchange and the coin name in the
    # alerts_blacklisted.txt file with a space in between like this:
    ####################
    # BTRX DOGE BTC
    # CPIA LIZI ETH
    ###################
    # and so on but without the pound signs
    with open("alerts_blacklist.txt", "r") as datafile:
        blacklisted = [
            # TODO: read as a map instead of a list
            x.strip().upper()
            for x in datafile.readlines()
            if not x.strip().startswith("#")
        ]

    return blacklisted


if __name__ == "__main__":
    main()
