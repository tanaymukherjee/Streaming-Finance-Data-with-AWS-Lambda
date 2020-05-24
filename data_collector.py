# Importing necessary libraries
import boto3
import os
import subprocess
import sys
import json

# Installing the yfinance package to get the stocks
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/tmp", 'yfinance'])
sys.path.append('/tmp')

# Import yfinance package to download stocks
import yfinance as yf

def lambda_handler(event, context):
    
    # Initialize boto3 client
    fh = boto3.client("firehose", "us-east-2")
    
    # Define required variables and arrays for compamny stocks we will analyze
    sdate = '2020-05-14'
    edate = '2020-05-15'
    granuality = '1m'
    stocks = ['fb', 'shop', 'bynd', 'nflx', 'pins', 'sq', 'ttd', 'okta', 'snap', 'ddog']
    
    # Fetch stock values for each company
    for stock in range(len(stocks)):
        records = yf.download(stocks[stock], start = sdate, end = edate, interval = granuality)
        data = []
        
        # Cleaning the data and store them as a dict
        for i in range(len(records)):
            output = {"High":records['High'][i],"Low":records['Low'][i],"Timestamp":records.index[i].strftime('%m/%d/%Y %X'),"Name":stocks[stock]}
            
            # Convert the data into JSON
            as_jsonstr = json.dumps(output)
    
            # Pass the stream info where the data should be stored as a single batch
            fh.put_record(
                DeliveryStreamName="finance-stream-tm", 
                Record = {'Data': as_jsonstr.encode('utf-8')})
            data.append(output)
            
    # Return the JSON file dump    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Done! Recorded: {as_jsonstr}')
    }