# Foreign Exchange Rates From Central Bank

# Demo

BASE_URL<br>
https://0syqhjy9p2.execute-api.ap-northeast-1.amazonaws.com/demo/<br>
ENDPOINT<br>
https://0syqhjy9p2.execute-api.ap-northeast-1.amazonaws.com/demo/prices<br>
QUERY PARAM<br>
date e.g. date="2023-02-14<br>

## Example
https://0syqhjy9p2.execute-api.ap-northeast-1.amazonaws.com/demo/prices?date=2022-11-17
## Headers
x-api-key: 85yBB7dWSjakpSclXBdr415BASvoVzxa3CkUPYe9

# AWS Services
1. Lambda
2. CloudWatch
2. DynamoDB
3. API Gateway

## AWS Setup
1. Create a Lambda Function select python3.8 runtime and add a layer with ```layer_packages.zip``` 
2. Create API gateway
3. Create REST API resource /prices along with GET method
4. Create API key, along with usage plan and connect API with key
5. Setup locally to create a dynamodb table exchange-rate locally or from dynamodb dashboard through create_dynamodb_table.py script
6. From cloudwatch, create a schedule for lambda function 16:30 CET time (Exchange rates gets update at this time) for every 24 hours 

## Local Setup
1. Create virtual env in python<br>
```virtualenv -p python3 env```
2. ```source env/bin/activate```
3. ```pip install -r requirements.txt```
4. Line 85 in lambda_handler.py replace dynamodb variable with following along with your aws credentials<br>
```
    dynamodb = boto3.resource(
        "dynamodb",
        aws_access_key_id='aws_access_key_id',
        aws_secret_access_key='aws_secret_access_key',
        region_name='region_name',
    )
```
5. To create dynamodb table<br>
```python create_dynamodb_table.py```
6. To populate dynamodb table with today's exchange rate or change Line 133 in lambda_handler.py <br>
with ```get_exchange_rates(dynamo_table, historic=True)``` to populate db with historic data<br>
```python local.py```
