"""Demo API routes — demo merchant management for judges."""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import boto3
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
SESSIONS_TABLE = os.getenv("DYNAMODB_SESSIONS_TABLE", "vyapari-sessions")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
dynamodb = boto3.resource("dynamodb", region_name=REGION)


# Demo merchant IDs (these will be seeded by seed_demo_data.py)
DEMO_MERCHANTS = [
    {
        "merchant_id": "demo_ramesh_001",
        "shop_name": "Ramesh General Store",
        "shop_name_hi": "रमेश जनरल स्टोर",
        "store_type": "kirana",
        "location": "Lajpat Nagar, Delhi",
        "product_count": 80,
        "icon": "🏪",
    },
    {
        "merchant_id": "demo_priya_002",
        "shop_name": "Priya's Spice Kitchen",
        "shop_name_hi": "प्रिया की रसोई",
        "store_type": "restaurant",
        "location": "Koramangala, Bengaluru",
        "product_count": 45,
        "icon": "🍛",
    },
    {
        "merchant_id": "demo_rajesh_003",
        "shop_name": "Rajesh Sweets & Namkeen",
        "shop_name_hi": "राजेश मिठाई और नमकीन",
        "store_type": "sweet_shop",
        "location": "Chandni Chowk, Delhi",
        "product_count": 60,
        "icon": "🍬",
    },
    {
        "merchant_id": "demo_anjali_004",
        "shop_name": "Anjali Bakery & Cafe",
        "shop_name_hi": "अंजलि बेकरी",
        "store_type": "bakery",
        "location": "Bandra West, Mumbai",
        "product_count": 35,
        "icon": "🥐",
    },
]


@router.get("/demo/merchants")
async def get_demo_merchants():
    """Return list of 4 pre-seeded demo merchants for judges.

    These merchants should be seeded via `python scripts/seed_demo_data.py`
    before running the demo.
    """
    return {
        "merchants": DEMO_MERCHANTS,
        "count": len(DEMO_MERCHANTS),
        "instructions": "Click any store card to start demo journey",
    }


@router.get("/demo/merchant/{merchant_id}")
async def get_demo_merchant_details(merchant_id: str):
    """Get full details of a demo merchant from DynamoDB."""
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    # Get merchant
    resp = merchants_table.get_item(Key={"merchant_id": merchant_id})
    merchant = resp.get("Item")

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail=f"Merchant {merchant_id} not found. Run 'python scripts/seed_demo_data.py' to seed demo data.",
        )

    # Get product count
    products_resp = products_table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
        Select="COUNT",
    )
    product_count = products_resp.get("Count", 0)

    return {
        "merchant": {
            "merchant_id": merchant.get("merchant_id"),
            "name": merchant.get("name"),
            "shop_name": merchant.get("shop_name"),
            "shop_type": merchant.get("shop_type"),
            "location": merchant.get("location", {}),
            "onboarding_status": merchant.get("onboarding_status"),
            "product_count": product_count,
        }
    }


class ResetRequest(BaseModel):
    session_id: Optional[str] = None
    merchant_id: Optional[str] = None


@router.post("/demo/reset")
async def reset_demo(req: ResetRequest):
    """Clear demo session data (chat messages, orders, sessions).

    Does NOT delete merchants or products (those are seeded and persist).

    Options:
    - If session_id provided: delete only that session
    - If merchant_id provided: delete all orders for that merchant
    - If neither: clear all sessions and orders (full reset)
    """
    sessions_table = dynamodb.Table(SESSIONS_TABLE)
    orders_table = dynamodb.Table(ORDERS_TABLE)

    deleted_sessions = 0
    deleted_orders = 0

    # Delete sessions
    if req.session_id:
        # Delete specific session
        try:
            sessions_table.delete_item(Key={"session_id": req.session_id})
            deleted_sessions = 1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
    else:
        # Delete all sessions
        try:
            scan_resp = sessions_table.scan(ProjectionExpression="session_id")
            for item in scan_resp.get("Items", []):
                sessions_table.delete_item(Key={"session_id": item["session_id"]})
                deleted_sessions += 1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to scan/delete sessions: {str(e)}")

    # Delete orders
    if req.merchant_id:
        # Delete orders for specific merchant
        try:
            query_resp = orders_table.query(
                IndexName="merchant-orders-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(req.merchant_id),
                ProjectionExpression="order_id",
            )
            for item in query_resp.get("Items", []):
                orders_table.delete_item(Key={"order_id": item["order_id"]})
                deleted_orders += 1
        except Exception as e:
            # If index doesn't exist, fall back to scan
            try:
                scan_resp = orders_table.scan(
                    FilterExpression=boto3.dynamodb.conditions.Attr("merchant_id").eq(req.merchant_id),
                    ProjectionExpression="order_id",
                )
                for item in scan_resp.get("Items", []):
                    orders_table.delete_item(Key={"order_id": item["order_id"]})
                    deleted_orders += 1
            except Exception as e2:
                raise HTTPException(status_code=500, detail=f"Failed to delete orders: {str(e2)}")
    else:
        # Delete all orders
        try:
            scan_resp = orders_table.scan(ProjectionExpression="order_id")
            for item in scan_resp.get("Items", []):
                orders_table.delete_item(Key={"order_id": item["order_id"]})
                deleted_orders += 1
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to scan/delete orders: {str(e)}")

    return {
        "status": "success",
        "deleted_sessions": deleted_sessions,
        "deleted_orders": deleted_orders,
        "message": "Demo data reset complete. Merchants and products preserved.",
    }


@router.post("/demo/seed/{merchant_id}")
async def seed_merchant_intelligence(merchant_id: str):
    """Populate intelligence data for a specific demo merchant.

    Creates:
    - 3-5 past orders with commission breakdown
    - Stock alerts for low-inventory products
    - Intelligence metadata for morning brief generation

    This endpoint is called automatically when entering demo mode,
    or manually via "Generate Morning Brief" button.
    """
    # Verify merchant exists
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)
    resp = merchants_table.get_item(Key={"merchant_id": merchant_id})
    merchant = resp.get("Item")

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail=f"Merchant {merchant_id} not found. Run seed_demo_data.py first.",
        )

    # Check if merchant is a demo merchant
    if merchant_id not in [m["merchant_id"] for m in DEMO_MERCHANTS]:
        raise HTTPException(
            status_code=400,
            detail="Intelligence seeding only works for demo merchants.",
        )

    # This will be implemented in seed_demo_data.py
    # For now, return a placeholder
    return {
        "status": "success",
        "merchant_id": merchant_id,
        "message": "Intelligence data seeding coming in seed_demo_data.py implementation",
        "todo": [
            "Generate 3-5 past orders",
            "Create stock alerts",
            "Generate demand forecast data",
        ],
    }


@router.get("/demo/status")
async def get_demo_status():
    """Check if demo merchants are seeded and ready."""
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    seeded = []
    missing = []

    for demo in DEMO_MERCHANTS:
        merchant_id = demo["merchant_id"]

        # Check if merchant exists
        resp = merchants_table.get_item(Key={"merchant_id": merchant_id})
        merchant = resp.get("Item")

        if merchant:
            # Check product count
            products_resp = products_table.query(
                IndexName="merchant-category-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
                Select="COUNT",
            )
            product_count = products_resp.get("Count", 0)

            seeded.append({
                "merchant_id": merchant_id,
                "shop_name": demo["shop_name"],
                "product_count": product_count,
            })
        else:
            missing.append({
                "merchant_id": merchant_id,
                "shop_name": demo["shop_name"],
            })

    return {
        "seeded": seeded,
        "missing": missing,
        "ready": len(missing) == 0,
        "message": "Run 'python scripts/seed_demo_data.py' to seed missing merchants" if missing else "All demo merchants ready!",
    }
