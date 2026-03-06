"""Order tools — CRUD operations, commission savings, daily summaries."""

import json
import uuid
import os
import random
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from dotenv import load_dotenv
from strands import tool

from agents.tools.ondc_protocol import (
    BUYER_APP_NAMES,
    calculate_aggregator_fees,
    calculate_ondc_fees,
)

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")

dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _dumps(obj) -> str:
    """JSON dumps with Decimal support for DynamoDB."""
    def default(o):
        if isinstance(o, Decimal):
            return int(o) if o == int(o) else float(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    return json.dumps(obj, default=default, ensure_ascii=False)


# Common Indian buyer names for simulation
BUYER_NAMES = [
    "Aarav Sharma", "Priya Patel", "Sneha Gupta", "Rahul Verma",
    "Anita Singh", "Vikram Joshi", "Meera Reddy", "Amit Kumar",
    "Pooja Nair", "Sanjay Mishra", "Kavita Rao", "Ravi Tiwari",
]


@tool
def create_order(merchant_id: str, items_json: str, customer_name: str, buyer_app: str) -> str:
    """Create a new ONDC order for a merchant.

    Args:
        merchant_id: The merchant's unique identifier
        items_json: JSON array of items, each with: product_id, name, qty, price
        customer_name: Name of the buyer
        buyer_app: Buyer app name (Paytm, Magicpin, Ola, etc.)

    Returns:
        JSON with order_id, total, commission details, and savings
    """
    table = dynamodb.Table(ORDERS_TABLE)
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    try:
        items = json.loads(items_json)
    except json.JSONDecodeError:
        return '{"status": "error", "message": "Invalid JSON in items_json"}'

    # Calculate total
    total = sum(item.get("price", 0) * item.get("qty", 1) for item in items)

    # Calculate ONDC fees and aggregator comparison
    distance_km = round(random.uniform(1.0, 5.0), 1)
    ondc_fees = calculate_ondc_fees(total, buyer_app, distance_km)
    swiggy_fees = calculate_aggregator_fees(total, "Swiggy")
    savings = round(swiggy_fees["total_deductions"] - ondc_fees["total_deductions"], 2)

    # Convert items for DynamoDB (floats → Decimal)
    db_items = []
    for item in items:
        db_items.append({
            "product_id": item.get("product_id", ""),
            "name": item.get("name", ""),
            "qty": item.get("qty", 1),
            "price": Decimal(str(item.get("price", 0))),
        })

    item_data = {
        "order_id": order_id,
        "merchant_id": merchant_id,
        "source": "ondc",
        "buyer_app": buyer_app,
        "customer_name": customer_name,
        "items": db_items,
        "total": Decimal(str(total)),
        "commission_ondc": Decimal(str(ondc_fees["commission_ondc"])),
        "commission_swiggy": Decimal(str(swiggy_fees["total_deductions"])),
        "savings": Decimal(str(savings)),
        "buyer_app_finder_fee": Decimal(str(ondc_fees["buyer_app_finder_fee"])),
        "seller_app_fee": Decimal(str(ondc_fees["seller_app_fee"])),
        "ondc_network_fee": Decimal(str(ondc_fees["ondc_network_fee"])),
        "logistics_partner": ondc_fees["logistics_partner"],
        "logistics_cost": Decimal(str(ondc_fees["logistics_cost"])),
        "logistics_eta": ondc_fees["logistics_eta"],
        "logistics_rider": ondc_fees["logistics_rider"],
        "gst_on_fees": Decimal(str(ondc_fees["gst_on_fees"])),
        "merchant_receives": Decimal(str(ondc_fees["merchant_receives"])),
        "status": "new",
        "created_at": now,
    }

    table.put_item(Item=item_data)

    return _dumps({
        "status": "success",
        "order_id": order_id,
        "customer_name": customer_name,
        "buyer_app": buyer_app,
        "items_count": len(items),
        "items": items,
        "total": total,
        # Backward-compatible fields
        "commission_ondc": ondc_fees["commission_ondc"],
        "commission_swiggy": swiggy_fees["total_deductions"],
        "savings": savings,
        # Detailed ONDC fee breakdown
        "ondc_fees": ondc_fees,
        "aggregator_comparison": swiggy_fees,
    })


@tool
def get_orders(merchant_id: str, status_filter: str = "") -> str:
    """Get all orders for a merchant, optionally filtered by status.

    Args:
        merchant_id: The merchant's unique identifier
        status_filter: Optional status to filter by (new, accepted, preparing, ready, delivered, cancelled). Leave empty for all orders.

    Returns:
        JSON with order list and summary stats
    """
    table = dynamodb.Table(ORDERS_TABLE)

    response = table.query(
        IndexName="merchant-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )

    items = response.get("Items", [])

    # Apply status filter if provided
    if status_filter:
        items = [o for o in items if o.get("status") == status_filter]

    # Sort by created_at descending (newest first)
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    orders = []
    total_revenue = 0
    total_savings = 0

    for order in items:
        total_revenue += float(order.get("total", 0))
        total_savings += float(order.get("savings", 0))

        orders.append({
            "order_id": order["order_id"],
            "customer_name": order.get("customer_name", ""),
            "buyer_app": order.get("buyer_app", ""),
            "items_count": len(order.get("items", [])),
            "total": order.get("total", 0),
            "status": order.get("status", ""),
            "savings": order.get("savings", 0),
            "created_at": order.get("created_at", ""),
        })

    return _dumps({
        "merchant_id": merchant_id,
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "total_savings": round(total_savings, 2),
        "orders": orders[:20],  # Limit to 20 most recent
    })


@tool
def update_order_status(order_id: str, new_status: str) -> str:
    """Update an order's status (accept, reject, prepare, deliver).

    Args:
        order_id: The order's unique identifier
        new_status: New status — one of: accepted, preparing, ready, delivered, cancelled

    Returns:
        JSON with update confirmation
    """
    table = dynamodb.Table(ORDERS_TABLE)
    now = datetime.now(timezone.utc).isoformat()

    valid_statuses = ["accepted", "preparing", "ready", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        return _dumps({"status": "error", "message": f"Invalid status. Must be one of: {valid_statuses}"})

    table.update_item(
        Key={"order_id": order_id},
        UpdateExpression="SET #status = :status, #updated = :now",
        ExpressionAttributeNames={"#status": "status", "#updated": "updated_at"},
        ExpressionAttributeValues={":status": new_status, ":now": now},
    )

    status_messages = {
        "accepted": "Order accepted! Taiyari shuru karein.",
        "preparing": "Order taiyar ho raha hai...",
        "ready": "Order ready for pickup/delivery!",
        "delivered": "Order delivered successfully!",
        "cancelled": "Order cancelled.",
    }

    return _dumps({
        "status": "updated",
        "order_id": order_id,
        "new_status": new_status,
        "message_hi": status_messages.get(new_status, ""),
    })


@tool
def calculate_savings(merchant_id: str) -> str:
    """Calculate total commission savings for a merchant — ONDC vs aggregators.

    Args:
        merchant_id: The merchant's unique identifier

    Returns:
        JSON with detailed savings breakdown comparing ONDC to Swiggy/Zomato
    """
    table = dynamodb.Table(ORDERS_TABLE)

    response = table.query(
        IndexName="merchant-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )

    items = response.get("Items", [])

    total_revenue = 0
    total_ondc_commission = 0
    total_swiggy_commission = 0
    order_count = 0

    for order in items:
        if order.get("status") != "cancelled":
            total_revenue += float(order.get("total", 0))
            total_ondc_commission += float(order.get("commission_ondc", 0))
            total_swiggy_commission += float(order.get("commission_swiggy", 0))
            order_count += 1

    total_savings = round(total_swiggy_commission - total_ondc_commission, 2)

    # Project monthly savings (assume current data represents ~1 week)
    monthly_projection = round(total_savings * 4, 2)
    yearly_projection = round(total_savings * 52, 2)

    return _dumps({
        "merchant_id": merchant_id,
        "total_orders": order_count,
        "total_revenue": round(total_revenue, 2),
        "ondc_commission": round(total_ondc_commission, 2),
        "swiggy_equivalent_commission": round(total_swiggy_commission, 2),
        "total_savings": total_savings,
        "monthly_projection": monthly_projection,
        "yearly_projection": yearly_projection,
        "savings_percentage": round((total_savings / total_revenue * 100), 1) if total_revenue > 0 else 0,
    })


@tool
def select_logistics_partner(store_type: str, item_types: str = "") -> str:
    """Select appropriate logistics partner based on store type and items.

    Args:
        store_type: Type of store (kirana, restaurant, sweet_shop, bakery)
        item_types: Comma-separated item types (e.g., "food,fragile")

    Returns:
        JSON with logistics partner recommendation, delivery time, and special handling
    """
    store_type_lower = store_type.lower()

    if store_type_lower == "kirana":
        return _dumps({
            "partner": "Shadowfax",
            "delivery_time": "30 min",
            "type": "hyperlocal",
            "rating": "food-rated" if "food" in item_types else "standard",
            "cost_base": 25
        })

    elif store_type_lower == "restaurant":
        return _dumps({
            "partner": "Shadowfax",
            "delivery_time": "45 min",
            "type": "food-delivery",
            "rating": "food-rated",
            "special_handling": "thermal packaging",
            "cost_base": 25
        })

    elif store_type_lower in ["sweet_shop", "bakery"]:
        return _dumps({
            "partner": "Dunzo",
            "delivery_time": "30 min",
            "type": "fragile-items",
            "rating": "food-rated",
            "special_handling": "careful handling for sweets/cakes",
            "cost_base": 25
        })

    else:
        return _dumps({
            "partner": "Dunzo",
            "delivery_time": "30 min",
            "type": "standard",
            "cost_base": 25
        })


@tool
def simulate_order(merchant_id: str) -> str:
    """Generate a realistic simulated ONDC order using products from the merchant's catalog.

    Args:
        merchant_id: The merchant's unique identifier

    Returns:
        JSON with the simulated order details including savings comparison
    """
    products_table = dynamodb.Table(PRODUCTS_TABLE)
    orders_table = dynamodb.Table(ORDERS_TABLE)

    # Fetch merchant's catalog
    response = products_table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )

    catalog = response.get("Items", [])
    available = [p for p in catalog if p.get("available", True)]

    if not available:
        return _dumps({"status": "error", "message": "No available products in catalog. Upload photos first."})

    # Pick 1-5 random products
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
    buyer_app = random.choice(BUYER_APP_NAMES)

    # Create order directly (avoid calling another @tool)
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    total = sum(item["price"] * item["qty"] for item in items)

    # Calculate ONDC fees and aggregator comparison
    distance_km = round(random.uniform(1.0, 5.0), 1)
    ondc_fees = calculate_ondc_fees(total, buyer_app, distance_km)
    swiggy_fees = calculate_aggregator_fees(total, "Swiggy")
    savings = round(swiggy_fees["total_deductions"] - ondc_fees["total_deductions"], 2)

    # Convert items for DynamoDB (floats → Decimal)
    db_items = []
    for item in items:
        db_items.append({
            "product_id": item["product_id"],
            "name": item["name"],
            "qty": item["qty"],
            "price": Decimal(str(item["price"])),
        })

    order_item = {
        "order_id": order_id,
        "merchant_id": merchant_id,
        "source": "ondc",
        "buyer_app": buyer_app,
        "customer_name": customer_name,
        "items": db_items,
        "total": Decimal(str(total)),
        "commission_ondc": Decimal(str(ondc_fees["commission_ondc"])),
        "commission_swiggy": Decimal(str(swiggy_fees["total_deductions"])),
        "savings": Decimal(str(savings)),
        "buyer_app_finder_fee": Decimal(str(ondc_fees["buyer_app_finder_fee"])),
        "seller_app_fee": Decimal(str(ondc_fees["seller_app_fee"])),
        "ondc_network_fee": Decimal(str(ondc_fees["ondc_network_fee"])),
        "logistics_partner": ondc_fees["logistics_partner"],
        "logistics_cost": Decimal(str(ondc_fees["logistics_cost"])),
        "logistics_eta": ondc_fees["logistics_eta"],
        "logistics_rider": ondc_fees["logistics_rider"],
        "gst_on_fees": Decimal(str(ondc_fees["gst_on_fees"])),
        "merchant_receives": Decimal(str(ondc_fees["merchant_receives"])),
        "status": "new",
        "created_at": now,
    }

    orders_table.put_item(Item=order_item)

    return _dumps({
        "status": "success",
        "order_id": order_id,
        "customer_name": customer_name,
        "buyer_app": buyer_app,
        "items_count": len(items),
        "items": items,
        "total": total,
        # Backward-compatible fields
        "commission_ondc": ondc_fees["commission_ondc"],
        "commission_swiggy": swiggy_fees["total_deductions"],
        "savings": savings,
        # Detailed ONDC fee breakdown
        "ondc_fees": ondc_fees,
        "aggregator_comparison": swiggy_fees,
    })
