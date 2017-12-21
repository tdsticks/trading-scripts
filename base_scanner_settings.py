from collections import namedtuple

Settings = namedtuple(
    "Settings",
    "days, skip, minutes, drop, six_candle_up, sensitivity, low_or_close, split_the_difference, delete_old_alerts, "
    + "exchange, minimum_volume, market")

settings = Settings(
    # how far back to look for bases. Suggested at least 14
    days=60,

    # this is how many candles back from now we ignore when scanning for bases; has to be at least 7
    skip=12,

    # candle time interval. suggested 60 for regular base breaks
    minutes=60,

    # percentage below detected bases to set alert so .96 is 4% down. Suggest at least .96 or .95
    drop=.95,

    # how much higher the sixth candles from the base should be relative to the base. Suggested at least 1.05
    six_candle_up=1.08,

    # A number 0-6 for how sensitive the scanner is to quality bases. Lower number allows higher quality bases but
    # less of them. 1, 2, or 3 seem to work best
    sensitivity=3,

    # whether you want bases based on the low or the close (bottom of wick or candle respectively). 3 gives you low
    # and 4 is close. (Also 0 is open and 1 is high if you want to go there)
    low_or_close=3,

    # Detects bases at 50% of wicks rather than the low or close prices. Setting this to True will cause the
    # low_or_close variable to be ignored
    split_the_difference=False,

    # If you want to delete all old alerts in alerts_set.txt for a coin before creating a new alert for that coin
    delete_old_alerts=True,

    exchange="BTRX",

    # Filters out all coins whose volume (in base coin in the last 24h) is less than this amount
    minimum_volume=1,

    market="BTC",
)
