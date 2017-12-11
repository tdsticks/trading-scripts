#!/usr/bin/python3

import time
import os
import decimal
import json
import requests
try:
    import z_manage_alerts
except Exception as e:
    print(e)
    input("You need to download z_manage_alerts.py from the project site")
    sys.exit()


alerted = []

while True:
    coinigy_alerts = z_manage_alerts.AlertManager._get_old_alerts()
    btrx_summaries = requests.get("https://bittrex.com/api/v1.1/public/getmarketsummaries")
    try:
        btrx_summaries = json.loads(btrx_summaries.text)
    except Exception as e:
        print(e)
        time.sleep(15)
        continue

    for alert in coinigy_alerts['data']['open_alerts']:
        alert['price'] = float(alert['price'])
        coinigy_mkt_name = alert['mkt_name'].split('/')[1] + '-' + alert['mkt_name'].split('/')[0]
        for summary in btrx_summaries['result']:
            if coinigy_mkt_name == summary['MarketName']:
                if alert['operator'] == '>' and summary['Last'] > alert['price'] and not alert in alerted:
                    print("\n" + summary['MarketName'] + " above " + str(round(decimal.Decimal(alert['price']), 8)))
                    print("https://www.coinigy.com/main/markets/BTRX/" + alert['mkt_name'])
                    print("https://bittrex.com/Market/Index?MarketName=" + summary['MarketName'])
                    os.system("mpv os.mp3  >/dev/null 2>&1")
                    alerted.append(alert)

                if alert['operator'] == '<' and summary['Last'] < alert['price'] and not alert in alerted:
                    print("\n" + summary['MarketName'] + " below " + str(round(decimal.Decimal(alert['price']), 8)))
                    print("https://www.coinigy.com/main/markets/BTRX/" + alert['mkt_name'])
                    print("https://bittrex.com/Market/Index?MarketName=" + summary['MarketName'])
                    os.system("mpv os.mp3  >/dev/null 2>&1")
                    alerted.append(alert)

    time.sleep(15) #Do not lower this below 2 or coinigy might end up banning you
