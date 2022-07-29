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
import random
#交易对列表
symbollist = ['btcusdt','ethusdt','solbtc','filbtc','filusdt','htusdt','adabtc','adausdt']
symbollist = ['COIN']
#模拟用户数
subs = 20
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
    mp.figure('', facecolor='#FF000000',figsize=(32, 24))
    mp.title('', fontsize=16)
    mp.xlabel('')
    mp.ylabel('')
    mp.tick_params(labelsize=0)
    mp.axis('off')
    
    # mp.grid(linestyle=':')
# 设置x轴刻度定位器
    ax = mp.gca()
    minutesLocator = md.MinuteLocator(interval=5)
    minutesLocator.MAXTICKS = 200
    ax.xaxis.set_major_locator(
        minutesLocator)
    ax.xaxis.set_major_formatter(
        md.DateFormatter('%d %b %Y %H:%M'))
    ax.xaxis.set_minor_locator(md.DayLocator())

    # # 控制实体与影线的颜色
    # rise = closing_prices >= opening_prices
    
    color = np.array(
        ['#FF000000' if x else 'white' for x in highest_prices])
    # ecolor = np.array(
    #     ['red' if x else 'green' for x in rise])

    # # 绘制实体
    mp.bar(dates, highest_prices - lowest_prices,
        0.001, lowest_prices, color='#FF000000',
        edgecolor='#FF000000', zorder=0)
    mode = random.randrange(0,2)
    #mode ==0 仅出现买单
    #mode ==1 仅出现卖单
    length = len(dates)
    mode=2
    if (mode == 0):
        cur = random.randrange(0,length-1)
        buyTime = [dates[cur]]
        buyPrice = [random.uniform(lowest_prices[cur],highest_prices[cur])]
        mp.scatter(buyTime,buyPrice,s=20*4,color='red',marker='o')
    elif (mode == 1):
        cur = random.randrange(0,length-1)
        sellTime = [dates[cur]]
        sellPrice = [random.uniform(lowest_prices[cur],highest_prices[cur])]
        mp.scatter(sellTime,sellPrice,s=20*4,color='green',marker='o')
    else:
        cur = random.randrange(0,length-1)
        buyTime = [dates[cur]]
        buyPrice = [random.uniform(lowest_prices[cur],highest_prices[cur])]
        mp.scatter(buyTime,buyPrice,s=20*4, color='red',marker='o')
        cur = random.randrange(0,length-1)
        sellTime = [dates[cur]]
        sellPrice = [random.uniform(lowest_prices[cur],highest_prices[cur])]
        mp.scatter(sellTime,sellPrice,color='green',marker='o')
    mp.legend()
    saveFile = './traindata/normal/out_'+symbol+'_'+str(num)+'.jpg'
    fig = mp.gcf()
    fig.set_size_inches(2.5, 1.5)
    fig.savefig(saveFile,dpi=100)

for symbol in symbollist:
    for i in range(1,subs):
        generateImage(i,symbol)
# # 绘制影线
# mp.vlines(dates, lowest_prices, highest_prices,
#           color=ecolor)
#mp.show()