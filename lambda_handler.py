"""
    v0.0 - REST API for fetching exchange rates from Euro Foreign Exchange

"""

import ast
from datetime import date, timedelta
import json

import uuid
import boto3
import requests
import xmltodict


def get_performance(last_price, current_price):
    """Function will calculate the percentage difference between last & current price."""
    return round(
        ((float(current_price) - float(last_price)) / float(last_price)) * 100, 2
    )


def get_exchange_rates(table_name, historic=False):
    """Function populates dynamodb with today's exchange rates or past 90 days if historic=True."""
    url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    if historic:
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"
    response = requests.get(url)
    data = xmltodict.parse(response.content)
    data = data["gesmes:Envelope"]["Cube"]["Cube"]
    if isinstance(data, dict):
        data = [data]
    data.reverse()
    last_date = ""
    for exchange_data in data:
        last_item = {}
        if last_date:
            last_item = ast.literal_eval(
                get_item_from_db(table_name, {"date": last_date})["Item"][
                    "exchange_info"
                ]
            )
            exchange_info = {
                item["@currency"]: (
                    float(item["@rate"]),
                    get_performance(item["@rate"], last_item[item["@currency"]][0]),
                )
                for item in exchange_data["Cube"]
            }
        else:
            exchange_info = {
                item["@currency"]: (float(item["@rate"]), 0.0)
                for item in exchange_data["Cube"]
            }
        table_name.put_item(
            Item={
                "id": uuid.uuid4().hex,
                "date": exchange_data["@time"],
                "exchange_info": str(exchange_info),
            }
        )

        last_date = exchange_data["@time"]


def get_item_from_db(table_name, key):
    """Function will fetch item from dynamodb using given key object."""
    return table_name.get_item(Key=key)


def get_response(status_code, body):
    """Function will generate a response to return."""
    return {"statusCode": status_code, "body": body}


def validate_date(date_text):
    """Function will help us identify the date text is a date format."""
    try:
        date.fromisoformat(date_text)
    except ValueError:
        return False
    return True


def lambda_handler(event, context):
    """This is a Lambda Function."""
    dynamodb = boto3.resource("dynamodb")
    # For local development
    # dynamodb = boto3.resource(
    #     "dynamodb",
    #     aws_access_key_id='aws_access_key_id',
    #     aws_secret_access_key='aws_secret_access_key',
    #     region_name='region_name',
    # )
    dynamo_table = dynamodb.Table("exchange-rate")
    params = event.get("queryStringParameters")
    if event.get("path") in ["/prices", "/prices/"]:
        if params and params.get("date"):
            if validate_date(params.get("date")) is False:
                return get_response(400, "Incorrect date format, should be YYYY-MM-DD")
            response = get_item_from_db(dynamo_table, {"date": params.get("date")})
            if response.get("Item", None) is None:
                return get_response(
                    400,
                    "Data isn't availbale for the provided date. Make sure it's a weekday.",
                )
        else:
            current_date = date.today()
            if current_date.weekday() in [5, 6]:
                current_date = current_date - timedelta((current_date.weekday() - 5 + 1))
            response = get_item_from_db(dynamo_table, {"date": current_date.strftime("%Y-%m-%d")})
            if response.get("Item", None) is None:
                current_date = current_date - timedelta(1)
                if current_date.weekday() in [5, 6]:
                    current_date = current_date - timedelta(
                        (current_date.weekday() - 5 + 1)
                    )
                response = get_item_from_db(
                    dynamo_table, {"date": current_date.strftime("%Y-%m-%d")}
                )

        if response.get("Item"):
            response["Item"].pop("id", None)
            return get_response(200, json.dumps(response.get("Item")))
        return get_response(400, "Data isn't availbale for the provided date. Make sure it's a weekday.")
    else:
        get_exchange_rates(dynamo_table, True)
        return get_response(200, "Data processed successfully.")
