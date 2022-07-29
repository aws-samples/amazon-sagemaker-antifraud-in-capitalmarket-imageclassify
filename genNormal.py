# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import unicode_literals
from base64 import decode
from datetime import datetime
import numpy as np
import requests
import csv
import random
import heapq
# symbollist = ['btcusdt','ethusdt','solbtc','atometh','filbtc','filusdt','htusdt','adabtc','adausdt','iriseth']
symbollist = ['COIN']


for symbol in symbollist:
    
    filename = './kline/'+symbol +'.csv'
    dates,  highest_prices, \
    lowest_prices = np.genfromtxt(
        filename, delimiter=',',
        usecols=(0, 1, 2), unpack=True,
        dtype=('|U20','f8','f8'),
        encoding='utf-8-sig',
        skip_header=1
        )
    print(filename)
    print(dates)
    header = ['time','price']
    for i in range(1,100):
        sellname = './sell/'+'sell_'+symbol+'_'+str(i)+'.csv'
        buyname = './buy/'+'buy_'+symbol+'_'+str(i)+'.csv'
        times = random.randrange(2,4)
        print("time:",times)
        with open(buyname,'w+') as f:
            buywriter = csv.writer(f)
            buywriter.writerow(header)
        with open(sellname,'w+') as f:
            sellwriter = csv.writer(f)
            sellwriter.writerow(header)
        for j in range(1,times):
            idx = random.randrange(1,len(dates))
            
            print("idx:",idx)
            row = []
            row.append(dates[idx])
            riseAmount = highest_prices[idx] - lowest_prices[idx]

            
            rate = random.randrange(90,100)
            mockSellprice = lowest_prices[idx]+riseAmount*rate/100
            row.append(round(mockSellprice,4))
            print(row)
            with open(sellname,'a+') as f:
                sellwriter = csv.writer(f)
                sellwriter.writerow(row)

            row = []
            row.append(dates[idx])
            riseAmount = highest_prices[idx] - lowest_prices[idx]
            rate = random.randrange(0,10)
            mockBuyprice = lowest_prices[idx]+riseAmount*rate/100
            row.append(round(mockBuyprice,4))
            print(row)
            with open(buyname,'a+') as f:
                buywriter = csv.writer(f)
                buywriter.writerow(row)

   



