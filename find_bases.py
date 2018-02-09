# -*- coding: utf-8 -*-
#!/usr/bin/python3

__author__ = 'steves'

import json
import time
from urllib.request import urlopen, Request


import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

candleLimit = 120

def loadCoinigyFeed():
    exch = "GDAX"
    coin = "BTC"
    mkt = "USD"
    minutes = 60
    days = 60

    candlesStr = "https://www.coinigy.com/getjson/chart_feed/" + \
                 exch + "/" + \
                 coin + "/" + \
                 mkt + "/" + \
                 str(minutes) + "/" + \
                 str(round(time.time() - (int(86400 * days)))) + "/" + \
                 str(round(time.time()))
    print("candlesStr", candlesStr)

    candles = urlopen(candlesStr).read().decode("utf-8")
    # print("candles", candles)

    candlesJSON = json.loads(candles)
    print("candlesJSON", candlesJSON)

def loadJsonCandles():

    jsonFile = "./candles.json"

    f = open(jsonFile)

    lines = f.readlines()[0].replace("[[", "").replace("]]", "")
    # print("lines", lines)

    parseLines = lines.split("], [")
    # print("parseLines", parseLines)

    dateList = []
    lowList = []
    volList = []

    for l, line in enumerate(parseLines):
        # print(line)

        if l <= candleLimit:

            splitLine = line.replace(", '",",").replace("', '", ",").replace("', ", ",").replace("',",",").split(",")
            # print(splitLine)

            #   OpenTime      Open                High                Low                 Close              Volume             CloseTime
            # ['1512313200', '11635.9700000000', '11798.5000000000', '11625.0100000000', '11755.0000000000','1174.8621198800', '1512316875']

            dateStr = int(splitLine[0])
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dateStr))
            # print(date)

            low = splitLine[3]
            vol = splitLine[5]

            dateList.append(date)
            lowList.append(low)
            volList.append(vol)

    # print(len(lowList))
    # print(dateList)

    return [dateList, lowList, volList]

def parseCandleFeed(dataLists):
    # print("dataLists:", dataLists)

    dateList = dataLists[0]
    lowCandleList = dataLists[1]
    volList = dataLists[2]

    candleCount = len(lowCandleList)
    print("candleCount",candleCount)

    # print("dateList:", dateList)
    # print("lowCandleList:", lowCandleList)
    # print("volList:", volList)

    # return

    # direction
    dir = ""
    volDir = ""

    volAvg = 0

    for i, candle in enumerate(lowCandleList):
        vol = float(volList[i])
        volAvg = vol + volAvg

    calcVolAvg = volAvg / candleCount

    print("volAvg", volAvg)
    print("calcVolAvg", calcVolAvg)




    for i, candle in enumerate(lowCandleList):

        vol = float(volList[i])

        nextI = i + 1
        # print(i, nextI, len(lowCandleList))

        if len(lowCandleList) > nextI:
            nextCandle = float(lowCandleList[nextI])
            # print(i, candle, nextCandle)

            calcDir = nextCandle - float(candle)
            # print(i, candle, nextCandle, calcDir)

            calVolPer = (vol / calcVolAvg) * 100

            if calVolPer > 100.00:
                volDir = "up"
            elif calcVolAvg < 100.00:
                volDir = "down"
            # else:
            #     volDir = "equal"

            print(vol, calVolPer, volDir)


            if calcDir >= 0:
                dir = "up"
            elif calcDir <= 0:
                dir = "down"
            elif calcDir == 0:
                dir = "even"

            # print(i, candle, nextCandle, calcDir, dir, vol, volDir)




    # plt.plot(dateList, lowCandleList)
    # plt.xlabel('low candles')
    # plt.ylabel('date')
    # plt.show()

def main():

    [dateList, lowList, volList] = loadJsonCandles()
    # print("dateList:", dateList)
    # print("lowList:", lowList)
    # print("volList:", volList)

    parseCandleFeed([dateList, lowList, volList])

if __name__ == "__main__":

    main()