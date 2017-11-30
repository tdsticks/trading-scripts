#!/usr/bin/python3

from urllib.request import urlopen
import time
import os
import decimal
import json

os.system("./z_get_alerts.php")
for line in open("alerts.txt"): print(line)

while True:
    summaries = urlopen("https://bittrex.com/api/v1.1/public/getmarketsummaries").read().decode("utf-8")
    summaries = json.loads(summaries)
    alerts = open("alerts.txt").readlines()
    for alert in alerts:
        alert = alert.split()
        alert[2] = float(alert[2].strip())
        for summary in summaries['result']:
            if alert[0] == summary['MarketName']:
                short_name = summary['MarketName'].split("-")[1]
                #print(summary['MarketName'])
                if alert[1] == '>' and summary['Last'] > alert[2]:
                    print()
                    print(summary['MarketName'] + " above " + str(decimal.Decimal(alert[2])))
                    print("https://www.coinigy.com/main/markets/BTRX/" + short_name + "/BTC")
                    print("https://bittrex.com/Market/Index?MarketName=BTC-" + short_name)
                    os.system("mpv os.mp3  >/dev/null 2>&1")
                    os.system("./get_alerts.php")
                if alert[1] == '<' and summary['Last'] < alert[2]:
                    print()
                    print(summary['MarketName'] + " below " + str(decimal.Decimal(alert[2])))
                    print("https://www.coinigy.com/main/markets/BTRX/" + short_name + "/BTC")
                    print("https://bittrex.com/Market/Index?MarketName=BTC-" + short_name)
                    os.system("mpv os.mp3  >/dev/null 2>&1")
                    os.system("./get_alerts.php")
    time.sleep(15)
