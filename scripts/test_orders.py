"""Test the Order Agent — order creation, savings, simulation, and agent integration."""

import sys
import json
sys.path.insert(0, ".")

import boto3
import os
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")


def get_test_merchant_id():
    """Find a merchant with products for testing."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants"))
    response = table.scan(Limit=5)
    merchants = response.get("Items", [])

    if not merchants:
        print("No merchants found. Run onboarding first.")
        sys.exit(1)

    # Find one with products
    products_table = dynamodb.Table(os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products"))
    for m in merchants:
        mid = m["merchant_id"]
        resp = products_table.query(
            IndexName="merchant-category-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(mid),
            Limit=1,
        )
        if resp.get("Items"):
            print(f"Using merchant: {m.get('name', 'Unknown')} ({m.get('shop_name', '')})")
            print(f"Merchant ID: {mid}\n")
            return mid

    mid = merchants[0]["merchant_id"]
    print(f"Warning: No merchant with products found. Using {mid}")
    return mid


def test_simulate_order(merchant_id: str):
    """Test 1: Simulate an ONDC order via direct function call."""
    print("=== Test 1: Simulate Order ===\n")

    import agents.tools.order_tools as ot

    # Access the underlying function through __wrapped__
    result = ot.simulate_order.__wrapped__(merchant_id=merchant_id)
    data = json.loads(result)

    if data.get("status") == "success":
        print(f"  Order ID: {data['order_id']}")
        print(f"  Customer: {data['customer_name']} via {data['buyer_app']}")
        print(f"  Items: {data['items_count']} | Total: ₹{data['total']}")
        print(f"  ONDC Commission: ₹{data['commission_ondc']}")
        print(f"  Swiggy would be: ₹{data['commission_swiggy']}")
        print(f"  Savings: ₹{data['savings']}")
        return data["order_id"]
    else:
        print(f"  Error: {data}")
        return None


def test_get_orders(merchant_id: str):
    """Test 2: Retrieve orders for a merchant."""
    print("\n=== Test 2: Get Orders ===\n")

    import agents.tools.order_tools as ot
    result = ot.get_orders.__wrapped__(merchant_id=merchant_id)
    data = json.loads(result)

    print(f"  Total Orders: {data.get('total_orders', 0)}")
    print(f"  Total Revenue: ₹{data.get('total_revenue', 0)}")
    print(f"  Total Savings: ₹{data.get('total_savings', 0)}")

    for order in data.get("orders", [])[:3]:
        print(f"  - {order['order_id'][:8]}... | {order['customer_name']} | ₹{order['total']} | {order['status']}")


def test_calculate_savings(merchant_id: str):
    """Test 3: Calculate commission savings."""
    print("\n=== Test 3: Calculate Savings ===\n")

    import agents.tools.order_tools as ot
    result = ot.calculate_savings.__wrapped__(merchant_id=merchant_id)
    data = json.loads(result)

    print(f"  Total Orders: {data.get('total_orders', 0)}")
    print(f"  Total Revenue: ₹{data.get('total_revenue', 0)}")
    print(f"  ONDC Commission: ₹{data.get('ondc_commission', 0)}")
    print(f"  Swiggy Equivalent: ₹{data.get('swiggy_equivalent_commission', 0)}")
    print(f"  Total Savings: ₹{data.get('total_savings', 0)}")
    print(f"  Monthly Projection: ₹{data.get('monthly_projection', 0)}/month")
    print(f"  Yearly Projection: ₹{data.get('yearly_projection', 0)}/year")


def test_update_order_status(order_id: str):
    """Test 4: Update order status."""
    if not order_id:
        print("\n=== Test 4: Skipped (no order_id) ===")
        return

    print(f"\n=== Test 4: Accept Order ({order_id[:8]}...) ===\n")

    import agents.tools.order_tools as ot
    result = ot.update_order_status.__wrapped__(order_id=order_id, new_status="accepted")
    data = json.loads(result)
    print(f"  Status: {data.get('status')}")
    print(f"  New Status: {data.get('new_status')}")
    print(f"  Message: {data.get('message_hi')}")


def test_order_agent(merchant_id: str):
    """Test 5: Order Agent conversation."""
    print("\n=== Test 5: Order Agent Conversation ===\n")

    from agents.order_agent import create_order_agent

    agent = create_order_agent()

    print(f"Prompt: 'Generate a demo order for merchant {merchant_id[:8]}...'")
    result = agent(
        f"Generate a demo ONDC order for merchant_id={merchant_id}. "
        f"Use simulate_order tool to create it, then show the order notification in Hindi with savings comparison."
    )
    print(f"\nAgent response:\n{result.message}\n")


if __name__ == "__main__":
    merchant_id = get_test_merchant_id()

    order_id = test_simulate_order(merchant_id)
    test_get_orders(merchant_id)
    test_calculate_savings(merchant_id)
    test_update_order_status(order_id)
    test_order_agent(merchant_id)

    print("\n=== All Order Tests Complete ===")
