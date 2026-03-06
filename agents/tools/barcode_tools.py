"""Barcode lookup tools — Open Food Facts + UPCitemdb for product identification."""

import json
import urllib.request
import urllib.error
from strands import tool


@tool
def lookup_barcode(barcode: str) -> str:
    """Look up a product by its barcode (EAN/UPC) using free product databases.

    Tries Open Food Facts first (free, unlimited), then UPCitemdb (free, 100/day).
    Returns product details including name, brand, category, and image if found.

    Args:
        barcode: EAN-13 or UPC barcode number (e.g., "8901030642029" for an Indian product)

    Returns:
        JSON with product details or not_found status
    """
    # Clean barcode — digits only
    clean_barcode = "".join(c for c in barcode if c.isdigit())

    if not clean_barcode or len(clean_barcode) < 8:
        return json.dumps({
            "status": "error",
            "message": "Invalid barcode. Must be at least 8 digits (EAN-8, EAN-13, or UPC).",
        }, ensure_ascii=False)

    # ── Try 1: Open Food Facts (free, no key, unlimited) ──
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{clean_barcode}.json"
        req = urllib.request.Request(url, headers={"User-Agent": "VyapariAI/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") == 1 and data.get("product"):
            p = data["product"]
            return json.dumps({
                "status": "found",
                "source": "open_food_facts",
                "barcode": clean_barcode,
                "product": {
                    "name": p.get("product_name", "") or p.get("product_name_en", ""),
                    "brand": p.get("brands", ""),
                    "category": p.get("categories", ""),
                    "quantity": p.get("quantity", ""),
                    "image_url": p.get("image_url", "") or p.get("image_front_url", ""),
                    "ingredients": p.get("ingredients_text", "")[:200],
                    "nutriscore": p.get("nutriscore_grade", ""),
                    "countries": p.get("countries", ""),
                },
            }, ensure_ascii=False)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        pass

    # ── Try 2: UPCitemdb (free tier, 100/day) ──
    try:
        url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={clean_barcode}"
        req = urllib.request.Request(url, headers={"User-Agent": "VyapariAI/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("items", [])
        if items:
            item = items[0]
            images = item.get("images", [])
            return json.dumps({
                "status": "found",
                "source": "upcitemdb",
                "barcode": clean_barcode,
                "product": {
                    "name": item.get("title", ""),
                    "brand": item.get("brand", ""),
                    "category": item.get("category", ""),
                    "description": item.get("description", "")[:200],
                    "image_url": images[0] if images else "",
                    "weight": item.get("weight", ""),
                    "ean": item.get("ean", ""),
                },
            }, ensure_ascii=False)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        pass

    # ── Not found in any database ──
    return json.dumps({
        "status": "not_found",
        "barcode": clean_barcode,
        "message": "Product not found in barcode databases. Please describe the product manually.",
    }, ensure_ascii=False)
