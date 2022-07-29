# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from __future__ import unicode_literals
from base64 import decode
from datetime import datetime
import requests
import csv

symbollist = ['COIN']
for symbol in symbollist:
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+symbol +'&interval=5min&apikey=Y14MIZ3T2PU4BXK1'
    r =requests.get(url)
    r_dict = r.json()
    

    filename = './kline/'+symbol +'.csv'
    header = ['time','high','low']
    with open(filename,'w+') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        r_detailData = r_dict['Time Series (5min)']
        cnt = 0
        for key in r_detailData:
            cnt = cnt+1
            if cnt == 80:
                break
            row = []
            row.append(key)
            data = r_detailData[key]
            row.append(data['2. high'])
            row.append(data['3. low'])
            writer.writerow(row)

