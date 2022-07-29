# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import unicode_literals
from base64 import decode
# -*- coding: utf-8 -*-
import numpy as np
import datetime as dt
import matplotlib.pyplot as mp
import matplotlib.dates as md
import pandas as pd
import heapq

from pyparsing import alphas


symbollist = ['COIN']
def generateImage(num,symbol):
    mp.cla()
    mp.clf()
    klineName = './kline/'+symbol+'.csv'
    dates,highest_prices, \
        lowest_prices = np.genfromtxt(
            klineName, delimiter=',',   
            usecols=(0, 1, 2), unpack=True,
            dtype=('|U20','f8','f8'),
            encoding='utf-8-sig',
            skip_header=1
            )
    dates = [dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in dates]
    # 绘制收盘价折线图
    mp.figure('', facecolor='blue',figsize=(32, 24))
    mp.title(symbol+' 5 minutes KLine', fontsize=16)
    mp.xlabel('DateTime')
    mp.ylabel('Price')
    mp.tick_params(labelsize=4)
    
    mp.axis('on')
    #mp.grid(linestyle=':')
# 设置x轴刻度定位器
    ax = mp.gca()
    minutesLocator = md.MinuteLocator(interval=5)
    minutesLocator.MAXTICKS = 3000
    ax.xaxis.set_major_locator(
        minutesLocator)
    ax.xaxis.set_major_formatter(
        md.DateFormatter('%d %b %Y %H:%M'))
    ax.xaxis.set_minor_locator(md.DayLocator())

    # # 控制实体与影线的颜色
    # rise = closing_prices >= opening_prices
    color = np.array(
        ['blue' if x else 'white' for x in highest_prices])
    # ecolor = np.array(
    #     ['red' if x else 'green' for x in rise])

    # # 绘制实体
    mp.bar(dates, highest_prices - lowest_prices,
        0.001, lowest_prices, color="blue",
        edgecolor='blue', zorder=0)
    
    buyFileName = './buy/'+'buy_'+symbol + '_'+'hacker'+'_'+str(num)+'.csv'
    hackerBuy,  buyPrices= np.genfromtxt(
            buyFileName, delimiter=',',
            usecols=(0, 1), unpack=True,
            skip_header=1,
            dtype=None,
            encoding='utf-8-sig'
            )
    
    if (hackerBuy.size == 1):
        aa = np.array2string(hackerBuy)
        aa = aa.replace('\'','')
        print(aa)
        hackerBuy = [dt.datetime.strptime(aa,'%Y-%m-%d %H:%M:%S')]
    
    else:
        hackerBuy = [dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in hackerBuy]      

    
    mp.scatter(hackerBuy,buyPrices,s=20*4,color='red',marker='o')
    sellFileName = './sell/'+'sell_'+symbol+'_'+'hacker'+'_'+str(num)+'.csv'
    hackerSell,  sellPrices= np.genfromtxt(
            sellFileName, delimiter=',',
            usecols=(0, 1), unpack=True,
            dtype=None,
            skip_header=1,
            encoding='utf-8-sig'
            )
    if (hackerSell.size == 1):
        aa = np.array2string(hackerSell)
        aa = aa.replace('\'','')
        print(aa)
        hackerSell = [dt.datetime.strptime(aa,'%Y-%m-%d %H:%M:%S')]
    else:
        hackerSell = [dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S') for x in hackerSell]      
    
    mp.scatter(hackerSell,sellPrices,s=20*4,color='green',marker='o')

    mp.legend()
    saveFile = './out_'+symbol+'_'+str(num)+'.jpg'
    fig = mp.gcf()
    fig.set_size_inches(10.5, 7.5)
    fig.savefig(saveFile,dpi=100)

for symbol in symbollist:
    for i in range(1,2):
        generateImage(i,symbol)
# # 绘制影线
# mp.vlines(dates, lowest_prices, highest_prices,
#           color=ecolor)
#mp.show()