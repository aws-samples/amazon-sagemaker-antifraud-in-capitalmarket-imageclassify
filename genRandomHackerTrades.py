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
#交易对数量
symbollist = ['COIN']
#每个交易对生成的黑客用户交易记录数
subs = 20
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

    
    minusResult = highest_prices - lowest_prices
    print("type of data",type(highest_prices))
    print("type of minusResult:",type(minusResult))
    sorted = heapq.nlargest(10,minusResult)
    print(sorted)
    aaaa = np.where(minusResult==sorted[2])

    print("sorted:",sorted)
    header = ['time','price']
    for i in range(1,subs):
        print(i)
        sellname = './sell/'+'sell_'+symbol+'_'+'hacker'+'_'+str(i)+'.csv'
        buyname = './buy/'+'buy_'+symbol+'_'+'hacker'+'_'+str(i)+'.csv'
        times = random.randrange(3,10)

        with open(buyname,'w+') as f:
            buywriter = csv.writer(f)
            buywriter.writerow(header)
        with open(sellname,'w+') as f:
            sellwriter = csv.writer(f)
            sellwriter.writerow(header)
        for j in range(1,times):  
            cur = random.randrange(0,9)
            idxList = np.where(minusResult==sorted[cur])
            idx = idxList[0][0]
            #print('j:',times,"idx:",idx)
            row = []
            row.append(dates[idx])
            riseAmount = highest_prices[idx] - lowest_prices[idx]
            if riseAmount/lowest_prices[idx] < 0.005:
                continue
            rate = random.randrange(90,100)
            mockSellprice = lowest_prices[idx]+riseAmount*rate/100
            row.append(mockSellprice)
            #print(row)
            with open(sellname,'a+') as f:
                sellwriter = csv.writer(f)
                sellwriter.writerow(row)
            row = []
            row.append(dates[idx])
            riseAmount = highest_prices[idx] - lowest_prices[idx]
            if riseAmount/lowest_prices[idx] < 0.005:
                continue
            rate = random.randrange(0,10)
            mockBuyprice = lowest_prices[idx]+riseAmount*rate/100
            row.append(mockBuyprice)
            #print(row)
            with open(buyname,'a+') as f:
                buywriter = csv.writer(f)
                buywriter.writerow(row)

   



