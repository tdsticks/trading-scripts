from collections import namedtuple

Param = namedtuple("Param", "value help")

user_settings = dict(
    days=Param(
        help="how far back to look for bases. Suggested at least 14",
        value=60,
    ),

    skip=Param(
        help="this is how many candles back from now we ignore when scanning for bases; has to be at least 7",
        value=12,
    ),

    minutes=Param(
        help="candle time interval. suggested 60 for regular base breaks",
        value=60,
    ),

    drop=Param(
        help="percentage below detected bases to set alert so .96 is 4%% down. Suggest at least .96 or .95",
        value=.95,
    ),

    six_candle_up=Param(
        help="how much higher the sixth candles from the base should be relative to the base. Suggested at least 1.05",
        value=.08,
    ),

    sensitivity=Param(
        help="A number 0-6 for how sensitive the scanner is to quality bases. Lower number allows higher quality bases but less of them. 1, 2, or 3 seem to work best",
        value=3,
    ),

    low_or_close=Param(
        help="whether you want bases based on the low or the close (bottom of wick or candle respectively). 3 gives you low and 4 is close. (Also 0 is open and 1 is high if you want to go there)",
        value=3,
    ),

    split_the_difference=Param(
        help="Detects bases at 50%% of wicks rather than the low or close prices. Setting this to True will cause the low_or_close variable to be ignored",
        value=False,
    ),

    delete_old_alerts=Param(
        help="If you want to delete all old alerts in alerts_set.txt for a coin before creating a new alert for that coin",
        value=True,
    ),

    exchange=Param(
        help="The exchange to use",
        value="BTRX",
    ),

    minimum_volume=Param(
        help="Filters out all coins whose volume (in base coin in the last 24h) is less than this amount",
        value=1,
    ),

    market=Param(
        help="Market to use",
        value="BTC",
    ),
)
