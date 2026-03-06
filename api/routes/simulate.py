"""POST /api/simulate-order/{merchant_id} — simulate an ONDC order with full fee breakdown."""

import json
import uuid
import random
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import boto3
import os
from dotenv import load_dotenv

from agents.tools.ondc_protocol import (
    calculate_ondc_fees,
    calculate_aggregator_fees,
    BUYER_APP_NAMES,
)

load_dotenv()

router = APIRouter()

REGION = os.getenv("AWS_REGION", "us-east-1")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")

dynamodb = boto3.resource("dynamodb", region_name=REGION)

BUYER_NAMES = [
    "Aarav Sharma", "Priya Patel", "Sneha Gupta", "Rahul Verma",
    "Anita Singh", "Vikram Joshi", "Meera Reddy", "Amit Kumar",
    "Pooja Nair", "Sanjay Mishra", "Kavita Rao", "Ravi Tiwari",
]


class SimulateOrderItem(BaseModel):
    product_id: str = ""
    name: str
    qty: int = 1
    price: float


class SimulateOrderRequest(BaseModel):
    items: Optional[list[SimulateOrderItem]] = None
    buyer_app: str = "Paytm"


class UpdateOrderStatusRequest(BaseModel):
    status: str


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    raise TypeError


@router.post("/simulate-order/{merchant_id}")
async def simulate_order(merchant_id: str, req: SimulateOrderRequest):
    """Simulate an ONDC order with full fee breakdown. No LLM needed."""
    orders_table = dynamodb.Table(ORDERS_TABLE)

    # If no items provided, pick random products from merchant's catalog
    if not req.items:
        products_table = dynamodb.Table(PRODUCTS_TABLE)
        response = products_table.query(
            IndexName="merchant-category-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
        )
        catalog = response.get("Items", [])
        available = [p for p in catalog if p.get("available", True)]

        if not available:
            return {"status": "error", "message": "No available products in catalog."}

        num_items = min(random.randint(2, 5), len(available))
        selected = random.sample(available, num_items)
        items = [
            {
                "product_id": p["product_id"],
                "name": p.get("name_en", p.get("name_hi", "Unknown")),
                "qty": random.randint(1, 3),
                "price": float(p.get("price", 0)),
            }
            for p in selected
        ]
    else:
        items = [item.model_dump() for item in req.items]

    # Calculate order
    total = sum(item["price"] * item["qty"] for item in items)
    buyer_app = req.buyer_app if req.buyer_app in BUYER_APP_NAMES else "Paytm"
    distance_km = round(random.uniform(1.0, 5.0), 1)

    ondc_fees = calculate_ondc_fees(total, buyer_app, distance_km)
    swiggy_fees = calculate_aggregator_fees(total, "Swiggy")
    zomato_fees = calculate_aggregator_fees(total, "Zomato")
    savings_vs_swiggy = round(swiggy_fees["total_deductions"] - ondc_fees["total_deductions"], 2)
    savings_vs_zomato = round(zomato_fees["total_deductions"] - ondc_fees["total_deductions"], 2)

    # Save order to DynamoDB
    order_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    customer_name = random.choice(BUYER_NAMES)

    db_items = [
        {
            "product_id": item.get("product_id", ""),
            "name": item["name"],
            "qty": item["qty"],
            "price": Decimal(str(item["price"])),
        }
        for item in items
    ]

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
        "savings": Decimal(str(savings_vs_swiggy)),
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

    return {
        "status": "success",
        "order_id": order_id,
        "customer_name": customer_name,
        "buyer_app": buyer_app,
        "items": items,
        "total": total,
        "ondc_fees": ondc_fees,
        "aggregator_comparison": {
            "swiggy": swiggy_fees,
            "zomato": zomato_fees,
        },
        "savings_vs_swiggy": savings_vs_swiggy,
        "savings_vs_zomato": savings_vs_zomato,
        "logistics": {
            "partner": ondc_fees["logistics_partner"],
            "rider_name": ondc_fees["logistics_rider"],
            "eta_minutes": ondc_fees["logistics_eta"],
            "distance_km": ondc_fees["logistics_distance_km"],
            "cost": ondc_fees["logistics_cost"],
        },
    }


@router.get("/orders/{merchant_id}")
async def get_merchant_orders(merchant_id: str):
    """Get all orders for a merchant."""
    orders_table = dynamodb.Table(ORDERS_TABLE)

    try:
        response = orders_table.query(
            IndexName="merchant-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
        )
        orders = response.get("Items", [])

        # Convert Decimal to float for JSON serialization
        orders_serialized = json.loads(json.dumps(orders, default=_decimal_default))

        return {
            "status": "success",
            "merchant_id": merchant_id,
            "order_count": len(orders_serialized),
            "orders": orders_serialized,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/orders/{order_id}/status")
async def update_order_status(order_id: str, req: UpdateOrderStatusRequest):
    """Update order status (accept, preparing, ready, delivered, cancelled)."""
    orders_table = dynamodb.Table(ORDERS_TABLE)

    valid_statuses = ["new", "accepted", "preparing", "ready", "delivered", "cancelled"]
    if req.status not in valid_statuses:
        return {
            "status": "error",
            "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        }

    try:
        # Update order status
        response = orders_table.update_item(
            Key={"order_id": order_id},
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": req.status},
            ReturnValues="ALL_NEW",
        )

        updated_order = response.get("Attributes", {})
        order_serialized = json.loads(json.dumps(updated_order, default=_decimal_default))

        return {
            "status": "success",
            "order_id": order_id,
            "new_status": req.status,
            "order": order_serialized,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
