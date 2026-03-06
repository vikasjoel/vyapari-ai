"""Intelligence tools — daily business insights, stock alerts, demand forecasting."""

import json
import random
import os
from datetime import datetime, timedelta, timezone

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")

dynamodb = boto3.resource("dynamodb", region_name=REGION)

# Indian festivals and events for demand forecasting
INDIAN_FESTIVALS = {
    "2026-03-06": {"name": "Holi", "categories": ["colors", "sweets", "snacks", "drinks"], "demand_multiplier": 3.0},
    "2026-10-24": {"name": "Diwali", "categories": ["sweets", "snacks", "dry_fruits", "oil", "decorations"], "demand_multiplier": 4.0},
    "2026-08-15": {"name": "Independence Day", "categories": ["snacks", "sweets", "beverages"], "demand_multiplier": 1.5},
    "2026-11-14": {"name": "Children's Day", "categories": ["chocolates", "snacks", "toys"], "demand_multiplier": 2.0},
    "2026-11-12": {"name": "Diwali", "categories": ["sweets", "dry_fruits", "oil", "snacks"], "demand_multiplier": 4.0},
    "2026-08-27": {"name": "Janmashtami", "categories": ["milk", "curd", "butter", "sweets"], "demand_multiplier": 2.5},
    "2026-03-25": {"name": "Holi", "categories": ["colors", "sweets", "thandai", "snacks"], "demand_multiplier": 3.0},
}


def _dumps(obj) -> str:
    """JSON dumps helper."""
    return json.dumps(obj, ensure_ascii=False)


@tool
def generate_morning_brief(merchant_id: str) -> str:
    """Generate morning business brief with yesterday's summary, stock alerts, and event predictions.

    Args:
        merchant_id: Merchant's unique ID

    Returns:
        JSON with morning brief including orders, revenue, stock alerts, and festival predictions
    """
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)
    orders_table = dynamodb.Table(ORDERS_TABLE)
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    # Get merchant details
    try:
        merchant_resp = merchants_table.get_item(Key={"merchant_id": merchant_id})
        merchant = merchant_resp.get("Item")
        if not merchant:
            return _dumps({"status": "error", "message": "Merchant not found"})
        merchant_name = merchant.get("name", "")
    except Exception:
        merchant_name = ""

    # Get yesterday's orders
    try:
        orders_resp = orders_table.query(
            IndexName="merchant-category-index",
            KeyConditionExpression="merchant_id = :mid",
            ExpressionAttributeValues={":mid": merchant_id}
        )
        orders = orders_resp.get("Items", [])
    except Exception:
        orders = []

    # Calculate yesterday's stats
    yesterday_orders = len(orders)
    yesterday_revenue = sum(float(o.get("total", 0)) for o in orders)
    yesterday_received = sum(float(o.get("merchant_receives", 0)) for o in orders)

    # Get stock alerts
    stock_alerts_data = json.loads(get_stock_alerts(merchant_id))
    stock_alerts = stock_alerts_data.get("alerts", [])

    # Get festival/event predictions
    forecast_data = json.loads(forecast_demand(merchant_id))
    upcoming_events = forecast_data.get("upcoming_events", [])

    return _dumps({
        "status": "success",
        "merchant_name": merchant_name,
        "yesterday": {
            "order_count": yesterday_orders,
            "revenue": round(yesterday_revenue, 2),
            "merchant_received": round(yesterday_received, 2)
        },
        "stock_alerts": stock_alerts,
        "upcoming_events": upcoming_events,
        "greeting": f"🌅 Good morning {merchant_name} ji!"
    })


@tool
def get_stock_alerts(merchant_id: str) -> str:
    """Get stock alerts for products running low or out of stock.

    Args:
        merchant_id: Merchant's unique ID

    Returns:
        JSON with list of stock alerts
    """
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    # Get merchant's products
    try:
        products_resp = products_table.query(
            IndexName="merchant-category-index",
            KeyConditionExpression="merchant_id = :mid",
            ExpressionAttributeValues={":mid": merchant_id}
        )
        products = products_resp.get("Items", [])
    except Exception:
        return _dumps({"status": "error", "message": "Could not fetch products"})

    if not products:
        return _dumps({"status": "success", "alerts": []})

    # Simulate stock alerts (for hackathon)
    alerts = []

    # Pick 2-3 products as "running low"
    if len(products) >= 3:
        running_low = random.sample(products, min(3, len(products)))
        for product in running_low:
            stock_level = random.randint(2, 8)
            days_to_stockout = random.randint(1, 3)
            alerts.append({
                "type": "running_low",
                "product_name": product.get("name_hi", product.get("name_en", "Unknown")),
                "product_id": product.get("product_id", ""),
                "stock_level": stock_level,
                "days_to_stockout": days_to_stockout,
                "message": f"⚠️ {product.get('name_hi', '')} — सिर्फ {stock_level} बचे, {days_to_stockout} दिन में खत्म हो जाएंगे"
            })

    # Pick 1 product as "out of stock"
    if len(products) >= 4:
        out_of_stock = random.choice([p for p in products if p.get("product_id") not in [a["product_id"] for a in alerts]])
        missed_orders = random.randint(2, 6)
        alerts.append({
            "type": "out_of_stock",
            "product_name": out_of_stock.get("name_hi", out_of_stock.get("name_en", "Unknown")),
            "product_id": out_of_stock.get("product_id", ""),
            "missed_orders": missed_orders,
            "message": f"❌ {out_of_stock.get('name_hi', '')} — out of stock! {missed_orders} orders miss हुए"
        })

    return _dumps({
        "status": "success",
        "alerts": alerts,
        "count": len(alerts)
    })


@tool
def compare_prices(merchant_id: str) -> str:
    """Compare merchant's prices with average ONDC prices.

    Args:
        merchant_id: Merchant's unique ID

    Returns:
        JSON with price comparison for key products
    """
    products_table = dynamodb.Table(PRODUCTS_TABLE)

    # Get merchant's products
    try:
        products_resp = products_table.query(
            IndexName="merchant-category-index",
            KeyConditionExpression="merchant_id = :mid",
            ExpressionAttributeValues={":mid": merchant_id}
        )
        products = products_resp.get("Items", [])
    except Exception:
        return _dumps({"status": "error", "message": "Could not fetch products"})

    if not products:
        return _dumps({"status": "success", "comparisons": []})

    # Simulate price comparisons (for hackathon)
    comparisons = []

    # Pick 3-5 products for comparison
    selected = random.sample(products, min(5, len(products)))

    for product in selected:
        merchant_price = float(product.get("price", 0))
        # Simulate average ONDC price (±10-20% of merchant price)
        variance = random.uniform(-0.2, 0.2)
        avg_ondc_price = round(merchant_price * (1 + variance), 2)
        diff = round(merchant_price - avg_ondc_price, 2)
        diff_percent = round((diff / avg_ondc_price) * 100, 1) if avg_ondc_price > 0 else 0

        comparison_type = "higher" if diff > 0 else "lower" if diff < 0 else "same"

        comparisons.append({
            "product_name": product.get("name_hi", product.get("name_en", "Unknown")),
            "merchant_price": merchant_price,
            "avg_ondc_price": avg_ondc_price,
            "difference": diff,
            "difference_percent": diff_percent,
            "comparison": comparison_type,
            "message": f"{'📈' if comparison_type == 'higher' else '📉' if comparison_type == 'lower' else '➡️'} {product.get('name_hi', '')}: आप ₹{merchant_price}, औसत ₹{avg_ondc_price} ({diff_percent:+.1f}%)"
        })

    return _dumps({
        "status": "success",
        "comparisons": comparisons,
        "count": len(comparisons)
    })


@tool
def forecast_demand(merchant_id: str) -> str:
    """Forecast demand based on upcoming festivals and events.

    Args:
        merchant_id: Merchant's unique ID

    Returns:
        JSON with demand forecast for next 7 days
    """
    merchants_table = dynamodb.Table(MERCHANTS_TABLE)

    # Get merchant's store type
    try:
        merchant_resp = merchants_table.get_item(Key={"merchant_id": merchant_id})
        merchant = merchant_resp.get("Item")
        if not merchant:
            return _dumps({"status": "error", "message": "Merchant not found"})
        store_type = merchant.get("shop_type", "kirana")
    except Exception:
        store_type = "kirana"

    # Check next 7 days for festivals
    today = datetime.now(timezone.utc).date()
    upcoming_events = []

    for i in range(7):
        check_date = today + timedelta(days=i)
        date_str = check_date.isoformat()

        if date_str in INDIAN_FESTIVALS:
            festival = INDIAN_FESTIVALS[date_str]
            days_away = i

            # Check if this festival is relevant for merchant's store type
            relevant_categories = festival["categories"]
            is_relevant = (
                store_type == "kirana" or
                (store_type == "restaurant" and any(cat in ["sweets", "snacks", "beverages"] for cat in relevant_categories)) or
                (store_type == "sweet_shop" and "sweets" in relevant_categories) or
                (store_type == "bakery" and any(cat in ["sweets", "snacks"] for cat in relevant_categories))
            )

            if is_relevant:
                upcoming_events.append({
                    "date": date_str,
                    "days_away": days_away,
                    "festival_name": festival["name"],
                    "demand_multiplier": festival["demand_multiplier"],
                    "relevant_categories": relevant_categories,
                    "message": f"{'🎉 आज' if days_away == 0 else f'🎉 {days_away} दिन में'} {festival['name']}! {festival['demand_multiplier']}x demand expected"
                })

    return _dumps({
        "status": "success",
        "upcoming_events": upcoming_events,
        "count": len(upcoming_events),
        "forecast_days": 7
    })
