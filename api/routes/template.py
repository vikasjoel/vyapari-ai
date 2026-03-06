"""Template API routes — fast product template loading and confirmation (no LLM)."""

import json
import uuid
import os
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

REGION = os.getenv("AWS_REGION", "us-east-1")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
dynamodb = boto3.resource("dynamodb", region_name=REGION)

# ── Load seed DB once ──
_SEED_DB: dict | None = None


def _get_seed_db() -> dict:
    global _SEED_DB
    if _SEED_DB is None:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vyapari_seed_db_v2.json")
        db_path = os.path.normpath(db_path)
        with open(db_path, "r", encoding="utf-8") as f:
            _SEED_DB = json.load(f)
    return _SEED_DB


@router.get("/template/{store_type}")
async def get_template(store_type: str, region: str = "north"):
    """Return template products for a store type, grouped by category.

    No LLM involved — direct JSON response from seed DB.
    """
    db = _get_seed_db()
    template = db.get("templates", {}).get(store_type)

    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown store type: {store_type}. Valid: kirana, restaurant, sweet_shop, bakery",
        )

    products = template["products"]

    # For restaurant, filter by region/cuisine
    if store_type == "restaurant":
        if region.lower() == "south":
            products = [p for p in products if p.get("cuisine", "").lower() == "south indian"]
        elif region.lower() == "north":
            products = [p for p in products if p.get("cuisine", "").lower() == "north indian"]

    # Determine grouping key
    if store_type == "kirana":
        group_key = "ondc_sub_category"
    elif store_type == "restaurant":
        group_key = "meal_type"
    elif store_type in ("sweet_shop", "bakery"):
        group_key = "item_type"
    else:
        group_key = "ondc_sub_category"

    # Group by category
    grouped: dict[str, list] = {}
    for p in products:
        cat = p.get(group_key, "Other")
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    return {
        "store_type": store_type,
        "label_en": template["label_en"],
        "label_hi": template["label_hi"],
        "ondc_domain": template["ondc_domain"],
        "region": region,
        "total_products": len(products),
        "categories": grouped,
    }


class ConfirmTemplateRequest(BaseModel):
    merchant_id: str
    store_type: str
    selected_product_ids: list[str]
    price_overrides: dict[str, int] = {}


@router.post("/template/confirm")
async def confirm_template(req: ConfirmTemplateRequest):
    """Confirm selected template products and batch-write to DynamoDB.

    Merchant selects products from template, optionally overrides prices,
    and this endpoint saves them to the vyapari-products table.
    """
    db = _get_seed_db()
    template = db.get("templates", {}).get(req.store_type)

    if not template:
        raise HTTPException(status_code=404, detail=f"Unknown store type: {req.store_type}")

    # Build lookup of seed products by product_id
    seed_lookup = {p["product_id"]: p for p in template["products"]}

    # Filter to selected products
    selected = []
    for pid in req.selected_product_ids:
        if pid in seed_lookup:
            selected.append(seed_lookup[pid])

    if not selected:
        raise HTTPException(status_code=400, detail="No valid products selected")

    # Write to DynamoDB
    table = dynamodb.Table(PRODUCTS_TABLE)
    now = datetime.now(timezone.utc).isoformat()
    saved_count = 0

    with table.batch_writer() as batch:
        for product in selected:
            product_id = str(uuid.uuid4())
            price = req.price_overrides.get(product["product_id"], product.get("mrp", 0))

            item = {
                "product_id": product_id,
                "merchant_id": req.merchant_id,
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
                              "eggless_available"):
                val = product.get(extra_key)
                if val is not None:
                    item[extra_key] = val

            batch.put_item(Item=item)
            saved_count += 1

    return {
        "status": "success",
        "merchant_id": req.merchant_id,
        "store_type": req.store_type,
        "products_saved": saved_count,
        "message": f"{saved_count} products saved to catalog",
    }
