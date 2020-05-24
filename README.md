# Streaming-Finance-Data-with-AWS-Lambda
For this project, you are tasked with provisioning a few Lambda functions to generate near real time finance data records for downstream processing and interactive querying.

This project leads us through the process of consuming “real time” data, processing the data and then dumping it in a manner that facilitates querying and further analysis, either in real time or near real time capacity.

In doing so, we will familiarize ourselves with a process that one can leverage in their professional or personal endeavors that require consumption of data that is “always on” and changing very quickly, in sub hour (and typically) sub minute intervals.

## Part 1: Architecture, Configuration and Setup
In this portion, we will configure the Kinesis firehose delivery stream, and also the lambda function for collection.

### A) Architecture
* ```Framework for this exercise```
![architecture](https://user-images.githubusercontent.com/6689256/82743708-2ce51d00-9d3d-11ea-9e34-54ff54f9379a.PNG)

### B) Configuration and Setup
* ```Setting up the Kinesis delivery stream```
![Kinesis_delivery stream](https://user-images.githubusercontent.com/6689256/82743664-73864780-9d3c-11ea-964a-3a8422c85b6a.PNG)

* ```Lambda configuration as the Data Collector```
![Data Collector Lambda configuration](https://user-images.githubusercontent.com/6689256/82743702-03c48c80-9d3d-11ea-9398-ed24855d307b.PNG)

* ```Initiating Athena services for querying```
![Athena Services](https://user-images.githubusercontent.com/6689256/82743875-53a45300-9d3f-11ea-9183-2a81a3b12710.PNG)

- [x] This module is completed


## Part 2: Transformation, Processing, Analyzing

### A) Transformation
#### 1. Lambda Function source code for collection:
* ```data_collector.py```
``` 
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
```

#### 2. Lambda Function :
* ```API endpoint```
``` 
https://wb3lb97r3e.execute-api.us-east-2.amazonaws.com/default/finance-stream-collector
```

### B) Processing
#### 1. Lambda Function source code for transformation:
* ```data_processor.py```
```
def lambda_handler(event, context):
    output_records = []
    for record in event["records"]:
        output_records.append({
            "recordId": record['recordId'],
            "result": "Ok",
            "data": record["data"] + "Cg==" 
        })
        
    return { "records": output_records }
```

#### 2. S3 data storage :
* ```S3 bucket URL```
``` 
https://s3.console.aws.amazon.com/s3/buckets/finance-stream/?region=us-east-2&tab=overview
```

### C) Analysis
#### 1. Query to fetch the highest stocks by hour for each stock on 14th May, 2020:
* ```data_collector.py```
``` 
SELECT upper(name) as Name, round(high,2) as High, timestamp as Timestamp, hour as Hour
from(
  select db.*,SUBSTRING(timestamp, 12, 2) as Hour, ROW_NUMBER() OVER(PARTITION BY name, SUBSTRING(timestamp, 12, 2) order by high) as rn
  FROM "21" db
  where timestamp between '05/14/2020 09:30:00' AND '05/14/2020 16:00:00'
)db1 where rn=1 order by name, timestamp
```

- [x] This module is completed


## Appendix
All the additional info about the project - the tools used, the servers required, system configuration, references, etc are included in this section.

### A) Project Specifications

#### 1. Application Summary
* ```System Specification:```
``` 
Operating System: Windows 10
RAM Size: 16 GB
Memory: 500 GB
```

* ```Tools Used:```
``` 
Programming Language: Python (Version 3.7)
Editor: Jupyter Notebook (Locally)
Platform: Amazon Web Services (AWS)
```

* ```Services Commissioned:```
``` 
Cloud Platform: AWS Lambda
Framework: AWS Kinesis
Data Storage: Amazon S3
Database Engine: AWS Athena
```

#### 2. Communication Channel
* ```Offline:```
``` 
Classrom: Room 10-155
Timing: Friday, 1800 to 2100 Hours
Address: Baruch Vertical Campus,
55, Lexington Avenue,
New York, USA
```

* ```Online:```
``` 
Slack: STA9760
Members: 53
```

### B) References

#### 1. Guide
* ```Prof. Taqqui Karim```
``` 
Subject: 9760 - Big Data Technologies
Session: Spring, 2020
```

#### 2. Links
- [Usage of yfinance package](https://github.com/ranaroussi/yfinance)
- [Putting data as a batch in AWS Kinesis](https://docs.aws.amazon.com/firehose/latest/APIReference/API_PutRecordBatch.html)
