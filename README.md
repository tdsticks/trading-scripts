# trading-scripts
Various scripts for trading cryptocurrency

#### adjust_alerts_public.php 
is for when you have a bunch of alerts in coinigy but you want to go to sleep. The script goes through each of your alerts and adjusts them down some percentage you specify in the file. When you wake up the next day, you can run the script again with a higher percentage to raise the ones that didn't go off back up.

#### z_auto_sell_when_bought.py
is a very simple script for when you have a buy on bittrex set but you want to go to sleep and you'd like that buy to automatically go up for sale if it triggers before you wake up. For it to work, you have to download the bittrex python api wrapper here: https://github.com/ericsomdahl/python-bittrex The script is run from a terminal with the first argument being the symbol for the coin like ETH and the second argument being what you want to sell the coin for like 0.45354329 or something. It'll keep checking every couple of minutes for a quantity above zero for that coin and when it sees something, it puts it up for sale. The script only works for BTC pairs since that's all I trade but it's just a line or two to change for it to work for USDT and ETH.

#### z_alerts.py
Sometimes Coinigy lags when alerting you on a price and this script is here to help that. It downloads all of your alerts from Coinigy and runs in a loop checking bittrex for the latest prices. If the conditions are met for one of your Coinigy alerts, z_alerts.py lets you know. Be sure to also download z_manage_alerts.py as well as api_keys.py and put your coinigy key and secret in api_keys.py as this is needed for z_alerts.py to work.

