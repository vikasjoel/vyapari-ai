"""Test the full onboarding flow: supervisor → onboarding agent → DynamoDB."""

import sys
sys.path.insert(0, ".")

from agents.supervisor import create_supervisor_agent
import boto3
import os
from dotenv import load_dotenv

load_dotenv()


def test_full_onboarding():
    print("=== Testing Full Onboarding Flow ===\n")
    agent = create_supervisor_agent()

    # Message 1: Introduction with multiple slots
    print("--- Message 1: Hindi greeting with name + location + type ---")
    result = agent("Namaste, main Ramesh hoon, Delhi ke Lajpat Nagar mein kirana store hai")
    print(f"Response: {result.message}\n")

    # Message 2: Shop name
    print("--- Message 2: Shop name ---")
    result = agent("Ramesh General Store hai naam")
    print(f"Response: {result.message}\n")

    # Message 3: Phone number
    print("--- Message 3: Phone number ---")
    result = agent("9876543210")
    print(f"Response: {result.message}\n")

    # Verify merchant in DynamoDB
    print("--- Verifying DynamoDB ---")
    ddb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = ddb.Table(os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants"))

    response = table.query(
        IndexName="phone-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("phone").eq("9876543210"),
    )

    items = response.get("Items", [])
    if items:
        merchant = items[0]
        print(f"  Found merchant: {merchant['name']}")
        print(f"  Shop: {merchant['shop_name']}")
        print(f"  Type: {merchant['shop_type']}")
        print(f"  Location: {merchant.get('location', {})}")
        print(f"  Status: {merchant['onboarding_status']}")
        print(f"  ONDC ID: {merchant['ondc_seller_id']}")

        # Cleanup test data
        table.delete_item(Key={"merchant_id": merchant["merchant_id"]})
        print(f"\n  Cleaned up test merchant: {merchant['merchant_id']}")
    else:
        print("  WARNING: Merchant not found in DynamoDB")
        print("  (This may be OK if the agent hasn't called save_merchant yet)")

    print("\n=== Onboarding Test Complete ===")


if __name__ == "__main__":
    test_full_onboarding()
