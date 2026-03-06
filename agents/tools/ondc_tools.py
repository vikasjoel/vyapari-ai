"""ONDC tools — Beckn schema generation and order simulation."""

import json
import uuid
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from dotenv import load_dotenv
from strands import tool


def _dumps(obj) -> str:
    """JSON dumps with Decimal support for DynamoDB."""
    def default(o):
        if isinstance(o, Decimal):
            return int(o) if o == int(o) else float(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    return json.dumps(obj, default=default)

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
dynamodb = boto3.resource("dynamodb", region_name=REGION)


@tool
def save_catalog(merchant_id: str, products_json: str) -> str:
    """Save a list of products to the merchant's catalog in DynamoDB.

    Args:
        merchant_id: The merchant's unique identifier
        products_json: JSON string containing array of products. Each product should have: name_en, name_hi, brand, variant, price, category, description_hi, is_loose_item, confidence

    Returns:
        JSON with save status and count of products saved
    """
    table = dynamodb.Table(PRODUCTS_TABLE)
    now = datetime.now(timezone.utc).isoformat()

    try:
        products = json.loads(products_json)
    except json.JSONDecodeError:
        return '{"status": "error", "message": "Invalid JSON in products_json"}'

    saved_count = 0
    saved_ids = []

    with table.batch_writer() as batch:
        for product in products:
            product_id = str(uuid.uuid4())
            item = {
                "product_id": product_id,
                "merchant_id": merchant_id,
                "name_en": product.get("name_en", "") or product.get("name", ""),
                "name_hi": product.get("name_hi", ""),
                "brand": product.get("brand", ""),
                "variant": product.get("variant", "") or product.get("size_weight", ""),
                "price": int(product.get("price", 0) or product.get("mrp", 0)),
                "category": product.get("category", "") or product.get("ondc_category", "Other"),
                "subcategory": product.get("subcategory", "") or product.get("ondc_sub_category", ""),
                "description_hi": product.get("description_hi", ""),
                "description_en": product.get("description_en", "") or product.get("description", ""),
                "image_url": product.get("image_url", ""),
                "available": True,
                "is_loose_item": product.get("is_loose_item", False),
                "ondc_item_id": f"ONDC-{product_id[:8].upper()}",
                "confidence": str(product.get("confidence", 1.0)),
                "source": product.get("source", "template"),
                "created_at": now,
                "updated_at": now,
            }

            # Optional fields from template products — only write if present and not None
            for extra_key in ("hsn_code", "gst_rate", "veg", "seed_product_id",
                              "prep_time", "serves", "cuisine", "meal_type",
                              "shelf_life", "storage", "item_type", "per_kg_price",
                              "eggless_available"):
                val = product.get(extra_key)
                if val is not None:
                    item[extra_key] = val

            batch.put_item(Item=item)
            saved_count += 1
            saved_ids.append(product_id)

    return _dumps({
        "status": "success",
        "merchant_id": merchant_id,
        "products_saved": saved_count,
        "product_ids": saved_ids[:5],
    })


@tool
def get_catalog(merchant_id: str) -> str:
    """Get all products in a merchant's catalog.

    Args:
        merchant_id: The merchant's unique identifier

    Returns:
        JSON with product list grouped by category
    """
    table = dynamodb.Table(PRODUCTS_TABLE)

    response = table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )

    items = response.get("Items", [])

    # Group by category
    categories = {}
    for item in items:
        cat = item.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "product_id": item["product_id"],
            "name_en": item.get("name_en", ""),
            "name_hi": item.get("name_hi", ""),
            "price": item.get("price", 0),
            "available": item.get("available", True),
            "brand": item.get("brand", ""),
        })

    return _dumps({
        "merchant_id": merchant_id,
        "total_products": len(items),
        "categories": categories,
    })


@tool
def update_product(product_id: str, field: str, value: str) -> str:
    """Update a single field of a product (e.g., price, available status).

    Args:
        product_id: The product's unique identifier
        field: Field to update (price, available, name_en, name_hi)
        value: New value (for price use number string like "32", for available use "true"/"false")

    Returns:
        JSON with update status
    """
    table = dynamodb.Table(PRODUCTS_TABLE)
    now = datetime.now(timezone.utc).isoformat()

    # Type conversion
    if field == "price":
        typed_value = int(value)
    elif field == "available":
        typed_value = value.lower() == "true"
    else:
        typed_value = value

    table.update_item(
        Key={"product_id": product_id},
        UpdateExpression="SET #field = :val, #updated = :now",
        ExpressionAttributeNames={"#field": field, "#updated": "updated_at"},
        ExpressionAttributeValues={":val": typed_value, ":now": now},
    )

    return _dumps({"status": "updated", "product_id": product_id, "field": field, "value": str(typed_value)})


@tool
def generate_beckn_schema(merchant_id: str, merchant_name: str, shop_name: str, city: str) -> str:
    """Generate ONDC Beckn protocol catalog schema for a merchant.

    Args:
        merchant_id: The merchant's unique identifier
        merchant_name: Merchant's name
        shop_name: Business name
        city: City where shop is located

    Returns:
        JSON string with Beckn-compliant catalog schema
    """
    table = dynamodb.Table(PRODUCTS_TABLE)

    response = table.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )

    items = response.get("Items", [])

    # Build Beckn catalog
    beckn_items = []
    for item in items:
        beckn_item = {
            "id": item.get("ondc_item_id", ""),
            "descriptor": {
                "name": item.get("name_en", ""),
                "short_desc": item.get("description_hi", ""),
                "long_desc": item.get("description_en", ""),
                "images": [{"url": item.get("image_url", "")}] if item.get("image_url") else [],
            },
            "price": {
                "currency": "INR",
                "value": str(item.get("price", 0)),
                "maximum_value": str(item.get("price", 0)),
            },
            "category_id": item.get("category", "Other"),
            "fulfillment_id": "F1",
            "location_id": "L1",
            "quantity": {
                "available": {"count": "999" if item.get("available", True) else "0"},
                "maximum": {"count": "10"},
            },
            "@ondc/org/returnable": True,
            "@ondc/org/cancellable": True,
            "@ondc/org/available_on_cod": False,
        }
        beckn_items.append(beckn_item)

    beckn_catalog = {
        "context": {
            "domain": "nic2004:52110",
            "action": "on_search",
            "country": "IND",
            "city": f"std:{city}",
        },
        "message": {
            "catalog": {
                "bpp/descriptor": {
                    "name": shop_name,
                    "short_desc": f"{merchant_name} ki dukaan on ONDC",
                },
                "bpp/providers": [
                    {
                        "id": merchant_id,
                        "descriptor": {"name": shop_name},
                        "locations": [
                            {"id": "L1", "city": {"name": city}},
                        ],
                        "items": beckn_items,
                    }
                ],
            }
        },
    }

    return _dumps({
        "status": "success",
        "beckn_schema": beckn_catalog,
        "items_count": len(beckn_items),
        "ondc_compliant": True,
    })
