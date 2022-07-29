# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import boto3
import sys
import base64
from botocore.exceptions import ClientError
import logging
import pymysql
import datetime
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as mp
import matplotlib.dates as md
import numpy as np

## global parameters
secret_name = "arn:aws:secretsmanager:us-east-1:xxxx:secret:db1-mjAB1B"
region_name = "us-east-1"
endpoint_name = 'antiFraud-imageclassification-ep--2022-05-14-xxxx'
bucket = "sagemaker-antifraud"


## get secrets database String
logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.session.Session()
client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
dynamodbClient = session.client("dynamodb")
try: 
    get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
except ClientError as e:
    logger.error("ERROR:Unexpected error: Could not get SecretString from SecretsManager.")
    logger.error(e)
    sys.exit()
    
## connect to database
logger.info(get_secret_value_response)
secrets = json.loads(get_secret_value_response["SecretString"])
rds_host  = secrets["host"]
name = secrets["username"]
password = secrets["password"]
db_name = secrets["dbname"]
try:
    logger.error("connect to database ......")
    conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=30)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
    
# FraudEvent class .
class FraudEvent :
    userid = ""
    fraudType = ""
    businessType = ""
    create_time = datetime.datetime.now()
    data = ""
    note = ""
    
    
# upload image to s3 bucket
def __upload_to_s3(channel, file):
    s3 = boto3.resource("s3")
    data = open(file, "rb")
    key = channel + "/" + file
    s3.Bucket(bucket).put_object(Key=key, Body=data)
    
# generate Image with user's trading data and 5minutes intraday kline in 24hours    
def __generateImage(userid,klines,deals):
    mp.cla()
    mp.clf()
    # 绘制收盘价折线图
    mp.figure('', facecolor='#FF000000',figsize=(32, 24))
    mp.title('', fontsize=16)
    mp.xlabel('')
    mp.ylabel('')
    mp.tick_params(labelsize=0)
    mp.axis('off')
    
    # 设置x轴刻度定位器
    ax = mp.gca()
    minutesLocator = md.MinuteLocator(interval=5)
    minutesLocator.MAXTICKS = 3000
    ax.xaxis.set_major_locator(
        minutesLocator)
    ax.xaxis.set_major_formatter(
        md.DateFormatter('%d %b %Y %H:%M'))
    ax.xaxis.set_minor_locator(md.DayLocator())
    
        
    klines = np.asarray(klines)
    dates = np.array([])
    highest_prices = np.array([])
    lowest_prices = np.array([])
    for record in klines:
        np.append(dates,record[0])
        np.append(highest_prices,record[1])
        np.append(lowest_prices,record[2])
        
        
    
    # # 绘制k线实体
    mp.bar(dates, highest_prices - lowest_prices,
        0.001, lowest_prices, color="#FF000000",
        edgecolor='#FF000000', zorder=0)
        
    hackerBuy = np.array([])
    hackerSell = np.array([])
    buyPrices = np.array([])
    sellPrices = np.array([])
    
    for dealrecord in deals :
        logger.info("dealrecord %s",dealrecord)
        logger.info("side:%s type is %s",dealrecord[2],type(dealrecord[2]))
        if dealrecord[2] == 'sell':
            logger.info("I'm here !!!!!")
            hackerSell = np.append(hackerSell,dealrecord[0])
            sellPrices = np.append(sellPrices,dealrecord[1])
        elif dealrecord[2] == "buy":
            hackerBuy = np.append(hackerBuy,dealrecord[0])
            buyPrices = np.append(buyPrices,dealrecord[1])
    
    logger.info("hackerSell:%s,\n sellPrices:%s",hackerSell,sellPrices)
    mp.scatter(hackerBuy,buyPrices,s=20*4,color='red',marker='o')
    mp.scatter(hackerSell,sellPrices,s=20*4,color='green',marker='o')
    mp.legend()
    saveFile = '/tmp/out_'+userid+'.jpg'
    fig = mp.gcf()
    fig.set_size_inches(2.5, 1.5)
    fig.savefig(saveFile,dpi=100)
    __upload_to_s3('fraud',saveFile)
    return saveFile
    
"""
Function: __create_fraud_event
Description:
    1. write fraud detection record to dynamodb.
input Parameters:
    fraudEvent : FraudEvent
return:
    void 
"""
def __create_fraud_event(fraudEvent):
    dynamodbClient.put_item(
        TableName='fraud_user_event',
        Item = {
            'userid':{
                'N':str(fraudEvent.userid),
            },
            'fraudType':{
                'S':fraudEvent.fraudType,
            },
            'businessType':{
                'S':fraudEvent.businessType,
            },
            'data':{'S':fraudEvent.data,},
            'note':{'S':fraudEvent.note,},
            'createTime':{'S':fraudEvent.create_time.strftime("%Y-%m-%d %H:%M:%S"),},
        })
        
"""
Function: get_latest_deal
Description:
    1.find latest deal by uid.
    2.get latest 2000 deals of trade pair of the latest deal.
input Parameters:
    uid : userid
        
return:
    deals tuple
    
        
"""
def __get_latest_deal(uid):
    
    with conn.cursor() as cur:
        cur.execute("select userid,symbol,deal_time,price,size,side from od_doge_btc_deal_log where userid=%s order by deal_time desc ",(uid,))
        result = cur.fetchone()
        #logger.info(result)
        
    logger.info(result)
    if result :
        logger.info(result)
        symbol = result[1]
        deal_time = result[2]
        
        logger.info("symbol %s. deal_time %s of type %s",symbol,deal_time,type(deal_time))
        
        with conn.cursor() as cur2:
            cur2.execute("select deal_time,price,side as side_trans,size from od_doge_btc_deal_log where symbol=%s and deal_time<=%s and userid=%s order by deal_time desc limit 10",(symbol,deal_time,uid,))
            deals = cur2.fetchall()
            logger.info(len(deals))
            return deals

def __get5mKline(symbol,deal_time):
    dealtime = dt.fromtimestamp(deal_time)
    start = dealtime - timedelta(hours=23)
    end = dealtime + timedelta(hours=1)
    start = dt.timestamp(start)
    end = dt.timestamp(end)
    with conn.cursor() as cur:
        cur.execute("select date_time,high,low from btc_usdt_kline where symbol=%s and date_time between %s and %s order by date_time desc ",(symbol ,start,end))
        result = cur.fetchall()
        
    logger.info(result)
    return result

def __infer_fraud(file_name):
    object_categories = [
        "hacker",
        "normal"
    ]
    runtime= boto3.client('runtime.sagemaker')
    with open(file_name, "rb") as f:
        payload = f.read()
        payload = bytearray(payload)
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name, ContentType="image/jpeg", Body=payload
    )
    result = response["Body"].read()
    # result will be in json format and convert it to ndarray
    result = json.loads(result)
    print("endpoint",endpoint_name)
    print("result:",result)
    # the result will output the probabilities for all classes
    # find the class with maximum probability and print the class index
    index = np.argmax(result)
    rslt = {"class":object_categories[index],"probability":result[index]}                            
    return rslt
       
    
def lambda_handler(event, context):
   
    logger.info("event:%s",event)
    for record in event['Records']:
        userEvent = json.loads(json.dumps(record['body']))
        logger.info("userEvent:%s",userEvent)
        
        logger.info("userid:%s",userEvent['userid'])
        deals = __get_latest_deal(userEvent['userid'])
        
        logger.info("deals:%s",deals)
        dealtime = deals[0][0]
    
        klines = __get5mKline("btcusdt",dt.timestamp(dealtime))
        filename = __generateImage(userEvent,klines,deals)
        result  = __infer_fraud(filename)
        if (result['class'] == 'hacker'):
            fraudEvent = FraudEvent()
            fraudEvent.userid = userEvent['userid']
            fraudEvent.fraudType = 'suspiciousTransaction'
            fraudEvent.data = str(result)
            fraudEvent.note = "create by AntifraudInfer"
            fraudEvent.businessType = userEvent['businessType']
            __create_fraud_event(fraudEvent)
    
    return {
        'statusCode': 200,
        'body': json.dumps('inference finished!')
    }
    
