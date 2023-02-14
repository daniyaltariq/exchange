"""
    To create Dynamodb table exchange-rate
"""

import boto3


if __name__ == "__main__":
    dynamodb = boto3.client(
        "dynamodb",
        aws_access_key_id="aws_access_key_id",
        aws_secret_access_key="aws_secret_access_key",
        region_name="region_name",
    )
    table = dynamodb.create_table(
        TableName="exchange-rate",
        KeySchema=[
            {"AttributeName": "date", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[{"AttributeName": "date", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
    )
