"""Simulate realistic ONDC orders for a merchant — used for demo and testing."""

import sys
import json
sys.path.insert(0, ".")

import boto3
import os
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")


def get_first_merchant():
    """Get the first merchant from DynamoDB for demo purposes."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants"))
    response = table.scan(Limit=1)
    items = response.get("Items", [])
    if items:
        return items[0]
    return None


def _simulate_one_order(merchant_id: str) -> dict:
    """Generate one simulated order directly (no @tool wrapper)."""
    import random
    from decimal import Decimal

    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    products_table = dynamodb.Table(os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products"))
    orders_table = dynamodb.Table(os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders"))

    from agents.tools.order_tools import COMMISSION_RATES, BUYER_APPS, BUYER_NAMES
    import uuid
    from datetime import datetime, timezone

    response = products_table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )
    catalog = response.get("Items", [])
    available = [p for p in catalog if p.get("available", True)]
    if not available:
        return {"status": "error", "message": "No available products"}

    num_items = min(random.randint(1, 5), len(available))
    selected = random.sample(available, num_items)

    items = []
    for product in selected:
        qty = random.randint(1, 3)
        items.append({
            "product_id": product["product_id"],
            "name": product.get("name_en", product.get("name_hi", "Unknown")),
            "qty": qty,
            "price": float(product.get("price", 0)),
        })

    customer_name = random.choice(BUYER_NAMES)
    buyer_app = random.choice(BUYER_APPS)
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    total = sum(i["price"] * i["qty"] for i in items)

    ondc_rate = random.uniform(COMMISSION_RATES["ondc"]["min"], COMMISSION_RATES["ondc"]["max"])
    swiggy_rate = random.uniform(COMMISSION_RATES["swiggy"]["min"], COMMISSION_RATES["swiggy"]["max"])
    commission_ondc = round(total * ondc_rate / 100, 2)
    commission_swiggy = round(total * swiggy_rate / 100, 2)
    savings = round(commission_swiggy - commission_ondc, 2)

    # Convert items for DynamoDB (floats → Decimal)
    db_items = [{"product_id": i["product_id"], "name": i["name"], "qty": i["qty"],
                 "price": Decimal(str(i["price"]))} for i in items]

    orders_table.put_item(Item={
        "order_id": order_id, "merchant_id": merchant_id, "source": "ondc",
        "buyer_app": buyer_app, "customer_name": customer_name, "items": db_items,
        "total": Decimal(str(total)), "commission_ondc": Decimal(str(commission_ondc)),
        "commission_swiggy": Decimal(str(commission_swiggy)), "savings": Decimal(str(savings)),
        "status": "new", "created_at": now,
    })

    return {
        "status": "success", "order_id": order_id, "customer_name": customer_name,
        "buyer_app": buyer_app, "items_count": len(items), "total": total,
        "commission_ondc": commission_ondc, "commission_swiggy": commission_swiggy,
        "savings": savings,
    }


def _get_savings(merchant_id: str) -> dict:
    """Calculate savings directly (no @tool wrapper)."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders"))

    response = table.query(
        IndexName="merchant-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )
    items = response.get("Items", [])
    total_revenue = sum(float(o.get("total", 0)) for o in items if o.get("status") != "cancelled")
    total_ondc = sum(float(o.get("commission_ondc", 0)) for o in items if o.get("status") != "cancelled")
    total_swiggy = sum(float(o.get("commission_swiggy", 0)) for o in items if o.get("status") != "cancelled")
    total_savings = round(total_swiggy - total_ondc, 2)

    return {
        "total_orders": len(items),
        "total_revenue": round(total_revenue, 2),
        "ondc_commission": round(total_ondc, 2),
        "swiggy_equivalent_commission": round(total_swiggy, 2),
        "total_savings": total_savings,
        "monthly_projection": round(total_savings * 4, 2),
        "yearly_projection": round(total_savings * 52, 2),
    }


def simulate_orders(merchant_id: str, count: int = 5):
    """Generate multiple simulated orders for a merchant."""
    print(f"=== Simulating {count} ONDC orders for merchant {merchant_id} ===\n")

    for i in range(count):
        print(f"--- Order {i + 1}/{count} ---")
        data = _simulate_one_order(merchant_id)

        if data.get("status") == "success":
            print(f"  Order ID: {data['order_id']}")
            print(f"  Customer: {data['customer_name']} via {data['buyer_app']}")
            print(f"  Items: {data['items_count']} | Total: ₹{data['total']}")
            print(f"  ONDC Commission: ₹{data['commission_ondc']}")
            print(f"  Swiggy would be: ₹{data['commission_swiggy']}")
            print(f"  Savings: ₹{data['savings']}")
        else:
            print(f"  Error: {data.get('message', 'Unknown error')}")
        print()

    # Show total savings
    savings = _get_savings(merchant_id)

    print("=== Savings Summary ===")
    print(f"  Total Orders: {savings['total_orders']}")
    print(f"  Total Revenue: ₹{savings['total_revenue']}")
    print(f"  ONDC Commission: ₹{savings['ondc_commission']}")
    print(f"  Swiggy Equivalent: ₹{savings['swiggy_equivalent_commission']}")
    print(f"  Total Savings: ₹{savings['total_savings']} 🎉")
    print(f"  Monthly Projection: ₹{savings['monthly_projection']}/month")
    print(f"  Yearly Projection: ₹{savings['yearly_projection']}/year")


if __name__ == "__main__":
    # Get merchant_id from args or find first merchant
    if len(sys.argv) > 1:
        mid = sys.argv[1]
    else:
        merchant = get_first_merchant()
        if merchant:
            mid = merchant["merchant_id"]
            print(f"Using merchant: {merchant.get('name', 'Unknown')} ({merchant.get('shop_name', '')})")
            print(f"Merchant ID: {mid}\n")
        else:
            print("No merchants found. Run onboarding first.")
            sys.exit(1)

    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    simulate_orders(mid, count)
    print("\n=== Simulation Complete ===")
