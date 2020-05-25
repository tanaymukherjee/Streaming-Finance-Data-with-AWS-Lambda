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
![Athena Services](https://user-images.githubusercontent.com/6689256/82781049-d522e080-9e26-11ea-9967-728778039c14.PNG)

- [x] This module is completed


## Part 2: Collection, Processing, Analyzing

### A) Collection
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
            output = {"high":records['High'][i],"low":records['Low'][i],"ts":records.index[i].strftime('%m/%d/%Y %X'),"name":stocks[stock]}
            
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

#### 2. Lambda Function URL:
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
#### 1. Query to fetch the highest stocks by hour for each stock on 14th May, 2020 and maintaining recurrence of high stocks:
* ```query.sql```
``` 
WITH CTE AS (
  SELECT *, ROW_NUMBER() over (PARTITION BY High, Hour ORDER BY Name, Hour, Timestamp) AS rn FROM (
    SELECT upper(db1.Name) AS Name, round(db1.High,2) AS High, db1.Hour as Hour, ts AS Timestamp FROM (
      SELECT name AS Name, max(high) AS High, substring(ts,12,2) AS Hour FROM  "04" 
      GROUP BY 1, 3
      ORDER BY 1, 3
      ) db1, "04" db2
    WHERE db1.Name = db2.name AND db1.Hour = substring(ts,12,2) AND db1.high = db2.High
    ORDER BY Name, Hour) db3)
    SELECT Name, High, Hour, Timestamp,
    Case
    when rn=1 then (SELECT count(*) FROM CTE t1 WHERE t1.High = t2.High AND t1.Hour = t2.Hour)
    else 0
    end AS Recurrence
    FROM CTE t2 ORDER BY Name, Hour, Timestamp
```

#### 2. Query to fetch the highest stocks by hour for each stock on 14th May, 2020 and picking only the first instance:
* ```query.sql```
```
SELECT Name, High, Hour, Timestamp FROM (
WITH CTE AS (
  SELECT *, ROW_NUMBER() over (PARTITION BY High, Hour ORDER BY Name, Hour, Timestamp) AS rn FROM (
    SELECT upper(db1.Name) AS Name, round(db1.High,2) AS High, db1.Hour as Hour, ts AS Timestamp FROM (
      SELECT name AS Name, max(high) AS High, substring(ts,12,2) AS Hour FROM  "04" 
      GROUP BY 1, 3
      ORDER BY 1, 3
      ) db1, "04" db2
    WHERE db1.Name = db2.name AND db1.Hour = substring(ts,12,2) AND db1.high = db2.High
    ORDER BY Name, Hour) db3)
    SELECT Name, High, Hour, Timestamp,
    Case
    when rn=1 then (SELECT count(*) FROM CTE t1 WHERE t1.High = t2.High AND t1.Hour = t2.Hour)
    else 0
    end AS Recurrence
    FROM CTE t2 ORDER BY Name, Hour, Timestamp) db4 WHERE Recurrence >= 1
```

#### 3. Additional Exercise: Visualizing the records in results.csv
* ```Analysis.ipynb```
```
It includes some plots to see the trend of high stock prices by day for each hour, distribution of all high stocks per hour, and also how they appear in a group plot when compared with each other. 
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
Programming Language: Python (Version 3.8)
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
