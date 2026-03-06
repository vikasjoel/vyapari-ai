"""GET /api/catalog/{merchant_id} — buyer-side catalog view."""

import os
import json
from decimal import Decimal
from fastapi import APIRouter, HTTPException

import boto3
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
dynamodb = boto3.resource("dynamodb", region_name=REGION)


def _serialize(obj):
    """Convert Decimal to int/float for JSON."""
    if isinstance(obj, Decimal):
        return int(obj) if obj == int(obj) else float(obj)
    raise TypeError(f"Not serializable: {type(obj)}")


@router.get("/catalog/{merchant_id}")
async def get_catalog(merchant_id: str):
    # Get merchant
    merchants = dynamodb.Table(MERCHANTS_TABLE)
    resp = merchants.get_item(Key={"merchant_id": merchant_id})
    merchant = resp.get("Item")
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    location = merchant.get("location", {})

    # Get products
    products = dynamodb.Table(PRODUCTS_TABLE)
    resp = products.query(
        IndexName="merchant-category-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("merchant_id").eq(merchant_id),
    )
    items = resp.get("Items", [])

    # Build response
    categories = sorted(set(p.get("category", "Other") for p in items))

    product_list = []
    for p in items:
        product_list.append({
            "product_id": p.get("product_id", ""),
            "name_hi": p.get("name_hi", ""),
            "name_en": p.get("name_en", ""),
            "brand": p.get("brand", ""),
            "price": int(p.get("price", 0)),
            "category": p.get("category", "Other"),
            "image_url": p.get("image_url", ""),
            "available": p.get("available", True),
            "confidence": float(p.get("confidence", 0)),
            "source": p.get("source", ""),
        })

    return {
        "merchant": {
            "shop_name": merchant.get("shop_name", ""),
            "location": f"{location.get('area', '')}, {location.get('city', '')}".strip(", "),
            "type": merchant.get("shop_type", ""),
            "product_count": len(items),
        },
        "products": product_list,
        "categories": categories,
        "ondc_compliant": True,
    }
