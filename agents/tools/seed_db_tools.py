"""Seed DB tools — template loading, fuzzy search, and category listing for v2 catalog creation."""

import json
import os
from difflib import SequenceMatcher
from strands import tool

# ── Singleton pattern: load JSON once at module level ──
_SEED_DB: dict | None = None


def _get_seed_db() -> dict:
    """Load and cache the seed product database."""
    global _SEED_DB
    if _SEED_DB is None:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vyapari_seed_db_v2.json")
        db_path = os.path.normpath(db_path)
        with open(db_path, "r", encoding="utf-8") as f:
            _SEED_DB = json.load(f)
    return _SEED_DB


@tool
def load_template(store_type: str, region: str = "north") -> str:
    """Load the product template for a given store type, organized by category.

    Use this when a merchant has been onboarded and wants to create their catalog
    from a pre-built template. Returns products grouped by category with images,
    prices, HSN codes, and all ONDC-required fields.

    Args:
        store_type: One of 'kirana', 'restaurant', 'sweet_shop', 'bakery'
        region: 'north' or 'south' — for restaurant, filters by cuisine. Ignored for other store types.

    Returns:
        JSON with products grouped by category, total count, and store metadata
    """
    db = _get_seed_db()
    template = db.get("templates", {}).get(store_type)

    if not template:
        return json.dumps({
            "status": "error",
            "message": f"Unknown store type: {store_type}. Valid types: kirana, restaurant, sweet_shop, bakery",
        }, ensure_ascii=False)

    products = template["products"]

    # For restaurant, filter by cuisine/region
    if store_type == "restaurant" and region.lower() == "south":
        products = [p for p in products if p.get("cuisine", "").lower() == "south indian"]
    elif store_type == "restaurant" and region.lower() == "north":
        products = [p for p in products if p.get("cuisine", "").lower() == "north indian"]

    # Group by category (ondc_sub_category for restaurant, item_type for sweet_shop/bakery, ondc_sub_category for kirana)
    grouped: dict[str, list] = {}
    if store_type == "kirana":
        group_key = "ondc_sub_category"
    elif store_type == "restaurant":
        group_key = "meal_type"
    elif store_type in ("sweet_shop", "bakery"):
        group_key = "item_type"
    else:
        group_key = "ondc_sub_category"

    for p in products:
        cat = p.get(group_key, "Other")
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    return json.dumps({
        "status": "success",
        "store_type": store_type,
        "label_en": template["label_en"],
        "label_hi": template["label_hi"],
        "ondc_domain": template["ondc_domain"],
        "region": region,
        "total_products": len(products),
        "categories": {cat: len(prods) for cat, prods in grouped.items()},
        "products_by_category": grouped,
    }, ensure_ascii=False)


@tool
def search_seed_db(query: str, store_type: str = "") -> str:
    """Fuzzy search the seed product database by name or brand.

    Use this when a merchant mentions a specific product by name and you want to
    find it in the database to add to their catalog.

    Args:
        query: Search query — product name, brand, or description (e.g., "Amul milk", "paneer tikka", "gulab jamun")
        store_type: Optional — limit search to a specific store type (kirana, restaurant, sweet_shop, bakery). Empty string searches all.

    Returns:
        JSON with matching products sorted by relevance score
    """
    db = _get_seed_db()
    query_lower = query.lower()
    results = []

    templates_to_search = {}
    if store_type and store_type in db.get("templates", {}):
        templates_to_search[store_type] = db["templates"][store_type]
    else:
        templates_to_search = db.get("templates", {})

    for st, template in templates_to_search.items():
        for product in template["products"]:
            # Check multiple fields for matching
            name_score = SequenceMatcher(None, query_lower, product.get("name", "").lower()).ratio()
            brand_score = SequenceMatcher(None, query_lower, product.get("brand", "").lower()).ratio()
            name_hi_score = SequenceMatcher(None, query_lower, product.get("name_hi", "").lower()).ratio()

            # Also check for substring match (boost)
            name_lower = product.get("name", "").lower()
            brand_lower = product.get("brand", "").lower()
            substring_boost = 0.3 if (query_lower in name_lower or query_lower in brand_lower) else 0.0

            best_score = max(name_score, brand_score, name_hi_score) + substring_boost

            if best_score > 0.4:
                results.append({
                    "score": round(best_score, 3),
                    "store_type": st,
                    "product": product,
                })

    # Sort by score descending, take top 10
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:10]

    return json.dumps({
        "status": "success",
        "query": query,
        "store_type_filter": store_type or "all",
        "matches_found": len(results),
        "results": results,
    }, ensure_ascii=False)


@tool
def get_categories(store_type: str) -> str:
    """Get category names with product counts for a store type.

    Use this to show the merchant what categories are available in their
    store template before loading the full template.

    Args:
        store_type: One of 'kirana', 'restaurant', 'sweet_shop', 'bakery'

    Returns:
        JSON with category names and product counts
    """
    db = _get_seed_db()
    template = db.get("templates", {}).get(store_type)

    if not template:
        return json.dumps({
            "status": "error",
            "message": f"Unknown store type: {store_type}. Valid types: kirana, restaurant, sweet_shop, bakery",
        }, ensure_ascii=False)

    products = template["products"]

    # Determine grouping key
    if store_type == "kirana":
        group_key = "ondc_sub_category"
    elif store_type == "restaurant":
        group_key = "meal_type"
    elif store_type in ("sweet_shop", "bakery"):
        group_key = "item_type"
    else:
        group_key = "ondc_sub_category"

    categories: dict[str, int] = {}
    for p in products:
        cat = p.get(group_key, "Other")
        categories[cat] = categories.get(cat, 0) + 1

    return json.dumps({
        "status": "success",
        "store_type": store_type,
        "label_en": template["label_en"],
        "label_hi": template["label_hi"],
        "total_products": len(products),
        "categories": categories,
    }, ensure_ascii=False)
