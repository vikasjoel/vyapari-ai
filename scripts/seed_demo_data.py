#!/usr/bin/env python3
"""Seed DynamoDB with 4 demo merchants for hackathon judges.

Usage:
    python scripts/seed_demo_data.py

Creates:
- 4 demo merchants (kirana, restaurant, sweet_shop, bakery)
- Pre-populated product catalogs from template
- Past orders with commission breakdown
- Intelligence data for morning briefs

Run this ONCE before deploying the demo.
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")

dynamodb = boto3.resource("dynamodb", region_name=REGION)


# Demo merchant configurations
DEMO_MERCHANTS = [
    {
        "merchant_id": "demo_ramesh_001",
        "name": "Ramesh Kumar",
        "name_hi": "रमेश कुमार",
        "shop_name": "Ramesh General Store",
        "shop_name_hi": "रमेश जनरल स्टोर",
        "shop_type": "kirana",
        "phone": "+919876543210",
        "location": {
            "area": "Lajpat Nagar",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110024",
            "lat": 28.5677,
            "lng": 77.2431,
        },
        "languages": ["hi", "en"],
        "ondc_seller_id": "ONDC-RAMESH-001",
        "onboarding_status": "live",
        "product_count_target": 80,
        "popularity_threshold": 6,  # Select products with popularity >= 6
    },
    {
        "merchant_id": "demo_priya_002",
        "name": "Priya Sharma",
        "name_hi": "प्रिया शर्मा",
        "shop_name": "Priya's Spice Kitchen",
        "shop_name_hi": "प्रिया की रसोई",
        "shop_type": "restaurant",
        "phone": "+919876543211",
        "location": {
            "area": "Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560034",
            "lat": 12.9352,
            "lng": 77.6245,
        },
        "languages": ["hi", "en", "kn"],
        "ondc_seller_id": "ONDC-PRIYA-002",
        "onboarding_status": "live",
        "product_count_target": 45,
        "popularity_threshold": 7,
        "cuisine": "north",  # For restaurant
    },
    {
        "merchant_id": "demo_rajesh_003",
        "name": "Rajesh Agarwal",
        "name_hi": "राजेश अग्रवाल",
        "shop_name": "Rajesh Sweets & Namkeen",
        "shop_name_hi": "राजेश मिठाई और नमकीन",
        "shop_type": "sweet_shop",
        "phone": "+919876543212",
        "location": {
            "area": "Chandni Chowk",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110006",
            "lat": 28.6506,
            "lng": 77.2303,
        },
        "languages": ["hi", "en"],
        "ondc_seller_id": "ONDC-RAJESH-003",
        "onboarding_status": "live",
        "product_count_target": 60,
        "popularity_threshold": 6,
    },
    {
        "merchant_id": "demo_anjali_004",
        "name": "Anjali Verma",
        "name_hi": "अंजलि वर्मा",
        "shop_name": "Anjali Bakery & Cafe",
        "shop_name_hi": "अंजलि बेकरी",
        "shop_type": "bakery",
        "phone": "+919876543213",
        "location": {
            "area": "Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400050",
            "lat": 19.0596,
            "lng": 72.8295,
        },
        "languages": ["hi", "en", "mr"],
        "ondc_seller_id": "ONDC-ANJALI-004",
        "onboarding_status": "live",
        "product_count_target": 35,
        "popularity_threshold": 7,
    },
]


def load_seed_db():
    """Load the seed database JSON."""
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "vyapari_seed_db_v2.json")
    db_path = os.path.normpath(db_path)
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def convert_floats_to_decimal(obj):
    """Recursively convert float to Decimal for DynamoDB."""
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def seed_merchant(merchant_config, seed_db):
    """Create one demo merchant with products."""
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    merchant_id = merchant_config["merchant_id"]
    store_type = merchant_config["shop_type"]

    print(f"\n{'='*60}")
    print(f"Seeding merchant: {merchant_config['shop_name']} ({store_type})")
    print(f"{'='*60}")

    # 1. Create merchant
    now = datetime.now(timezone.utc).isoformat()
    merchant_item = {
        "merchant_id": merchant_id,
        "name": merchant_config["name"],
        "shop_name": merchant_config["shop_name"],
        "shop_type": store_type,
        "phone": merchant_config["phone"],
        "location": convert_floats_to_decimal(merchant_config["location"]),
        "languages": merchant_config["languages"],
        "ondc_seller_id": merchant_config["ondc_seller_id"],
        "onboarding_status": merchant_config["onboarding_status"],
        "created_at": now,
        "updated_at": now,
    }

    try:
        merchants_table.put_item(Item=merchant_item)
        print(f"✅ Merchant created: {merchant_id}")
    except Exception as e:
        print(f"❌ Failed to create merchant: {e}")
        return

    # 2. Load template products
    template = seed_db.get("templates", {}).get(store_type)
    if not template:
        print(f"❌ No template found for store type: {store_type}")
        return

    all_products = template["products"]

    # Filter by cuisine for restaurant
    if store_type == "restaurant":
        cuisine = merchant_config.get("cuisine", "north")
        if cuisine == "north":
            all_products = [p for p in all_products if p.get("cuisine", "").lower() == "north indian"]
        elif cuisine == "south":
            all_products = [p for p in all_products if p.get("cuisine", "").lower() == "south indian"]

    # Limit to target count (no popularity filtering - seed DB doesn't have popularity_score)
    target_count = merchant_config.get("product_count_target", 50)
    all_products = all_products[:target_count]

    print(f"📦 Selected {len(all_products)} products from template")

    # 3. Batch write products
    saved_count = 0
    with products_table.batch_writer() as batch:
        for product in all_products:
            product_id = str(uuid.uuid4())
            price = product.get("mrp", 0)

            item = {
                "product_id": product_id,
                "merchant_id": merchant_id,
                "seed_product_id": product["product_id"],
                "name_en": product.get("name", ""),
                "name_hi": product.get("name_hi", ""),
                "brand": product.get("brand", ""),
                "variant": product.get("size_weight", ""),
                "price": int(price),
                "category": product.get("ondc_category", "Other"),
                "subcategory": product.get("ondc_sub_category", ""),
                "description_hi": product.get("name_hi", ""),
                "description_en": product.get("description", ""),
                "image_url": product.get("image_url", ""),
                "available": True,
                "is_loose_item": False,
                "veg": product.get("veg", True),
                "hsn_code": product.get("hsn_code", ""),
                "gst_rate": product.get("gst_rate", 0),
                "ondc_item_id": f"ONDC-{product_id[:8].upper()}",
                "confidence": "1.0",
                "source": "template",
                "created_at": now,
                "updated_at": now,
            }

            # Add store-type-specific fields
            for extra_key in ("prep_time", "serves", "cuisine", "meal_type",
                              "shelf_life", "storage", "item_type", "per_kg_price",
                              "eggless_available", "popularity_score"):
                val = product.get(extra_key)
                if val is not None:
                    item[extra_key] = val

            batch.put_item(Item=item)
            saved_count += 1

    print(f"✅ Products saved: {saved_count}")

    # 4. Create past orders (for intelligence)
    orders_created = seed_past_orders(merchant_id, merchant_config, seed_db)
    print(f"✅ Past orders created: {orders_created}")

    print(f"{'='*60}")
    print(f"✅ Merchant {merchant_config['shop_name']} fully seeded!")
    print(f"{'='*60}\n")


def seed_past_orders(merchant_id, merchant_config, seed_db):
    """Create 3-5 past orders for a merchant (for intelligence brief)."""
    orders_table = dynamodb.Table(ORDERS_TABLE)

    # Get some products for this merchant
    products_table = dynamodb.Table(PRODUCTS_TABLE)
    resp = products_table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
        Limit=20,
    )
    products = resp.get("Items", [])

    if not products:
        return 0

    # Create 4 orders (yesterday, 2 days ago, 3 days ago, 4 days ago)
    buyer_apps = ["Paytm", "Magicpin", "Ola", "PhonePe"]
    customer_names = ["Amit Kumar", "Sneha Singh", "Rajiv Sharma", "Pooja Verma"]

    orders_created = 0
    for i in range(4):
        order_id = str(uuid.uuid4())
        order_date = datetime.now(timezone.utc) - timedelta(days=i + 1)

        # Pick 2-4 random products
        import random
        num_items = random.randint(2, 4)
        order_products = random.sample(products, min(num_items, len(products)))

        items = []
        total = 0
        for p in order_products:
            qty = random.randint(1, 3)
            price = int(p.get("price", 0))
            items.append({
                "product_id": p.get("product_id"),
                "name": p.get("name_en", ""),
                "name_hi": p.get("name_hi", ""),
                "qty": qty,
                "price": price,
            })
            total += price * qty

        # ONDC commission: 8-10%
        commission_ondc = int(total * 0.09)

        # Swiggy/Zomato commission: 25-30%
        commission_swiggy = int(total * 0.27)

        savings = commission_swiggy - commission_ondc

        order_item = {
            "order_id": order_id,
            "merchant_id": merchant_id,
            "source": "ondc",
            "buyer_app": buyer_apps[i % len(buyer_apps)],
            "customer_name": customer_names[i % len(customer_names)],
            "items": items,
            "total": total,
            "commission_ondc": commission_ondc,
            "commission_swiggy": commission_swiggy,
            "savings": savings,
            "status": "delivered",
            "created_at": order_date.isoformat(),
        }

        try:
            orders_table.put_item(Item=order_item)
            orders_created += 1
        except Exception as e:
            print(f"⚠️  Failed to create order: {e}")

    return orders_created


def main():
    """Main seeding function."""
    print("\n" + "=" * 80)
    print("🌱 VYAPARI.AI DEMO DATA SEEDER")
    print("=" * 80)

    # Load seed database
    print("\n📂 Loading seed database...")
    seed_db = load_seed_db()
    print(f"✅ Seed database loaded: {len(seed_db.get('templates', {}))} store types")

    # Seed each merchant
    for merchant_config in DEMO_MERCHANTS:
        seed_merchant(merchant_config, seed_db)

    print("\n" + "=" * 80)
    print("🎉 ALL DEMO MERCHANTS SEEDED SUCCESSFULLY!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start API: uvicorn api.main:app --reload")
    print("2. Check status: curl http://localhost:8000/api/demo/status")
    print("3. Open frontend: http://localhost:5173")
    print("\n")


if __name__ == "__main__":
    main()
