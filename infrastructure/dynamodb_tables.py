"""Create DynamoDB tables for Vyapari.ai"""

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
dynamodb = boto3.client("dynamodb", region_name=REGION)


def create_merchants_table():
    """vyapari-merchants: PK=merchant_id, GSI on phone"""
    table_name = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "merchant_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "merchant_id", "AttributeType": "S"},
                {"AttributeName": "phone", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "phone-index",
                    "KeySchema": [
                        {"AttributeName": "phone", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Created table: {table_name}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table already exists: {table_name}")


def create_products_table():
    """vyapari-products: PK=product_id, GSI on merchant_id+category"""
    table_name = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "product_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "product_id", "AttributeType": "S"},
                {"AttributeName": "merchant_id", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "merchant-category-index",
                    "KeySchema": [
                        {"AttributeName": "merchant_id", "KeyType": "HASH"},
                        {"AttributeName": "category", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Created table: {table_name}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table already exists: {table_name}")


def create_orders_table():
    """vyapari-orders: PK=order_id, GSI on merchant_id"""
    table_name = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "order_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "order_id", "AttributeType": "S"},
                {"AttributeName": "merchant_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "merchant-index",
                    "KeySchema": [
                        {"AttributeName": "merchant_id", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Created table: {table_name}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table already exists: {table_name}")


def create_sessions_table():
    """vyapari-sessions: PK=session_id, GSI on merchant_id"""
    table_name = os.getenv("DYNAMODB_SESSIONS_TABLE", "vyapari-sessions")
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "session_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "session_id", "AttributeType": "S"},
                {"AttributeName": "merchant_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "merchant-index",
                    "KeySchema": [
                        {"AttributeName": "merchant_id", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Created table: {table_name}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table already exists: {table_name}")


if __name__ == "__main__":
    print("Creating DynamoDB tables for Vyapari.ai...")
    create_merchants_table()
    create_products_table()
    create_orders_table()
    create_sessions_table()
    print("Done!")
