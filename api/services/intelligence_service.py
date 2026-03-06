"""Intelligence Service — Generate business insights, stock alerts, and forecasts.

This service generates morning briefs, stock alerts, and demand forecasts
for merchants based on their order history and product catalog.
"""

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
dynamodb = boto3.resource("dynamodb", region_name=REGION)


def generate_morning_brief(merchant_id: str, language: str = "hi") -> Dict[str, Any]:
    """Generate morning brief for a merchant.

    Includes:
    - Greeting
    - Yesterday's stats (orders, revenue, commission saved)
    - Stock alerts (low-stock products)
    - Demand forecast (upcoming festivals/events)
    - Suggestions
    """
    # Get today's and yesterday's stats
    stats = get_merchant_stats(merchant_id)

    # Get stock alerts
    stock_alerts = get_stock_alerts(merchant_id)

    # Get demand forecast
    forecast = get_demand_forecast(merchant_id)

    # Generate suggestions
    suggestions = generate_suggestions(merchant_id, stats, stock_alerts)

    # Greeting
    hour = datetime.now(timezone.utc).hour
    if hour < 12:
        greeting = "Good Morning"
        greeting_hi = "सुप्रभात"
    elif hour < 17:
        greeting = "Good Afternoon"
        greeting_hi = "नमस्ते"
    else:
        greeting = "Good Evening"
        greeting_hi = "शुभ संध्या"

    return {
        "greeting": greeting,
        "greeting_hi": greeting_hi,
        "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "stats": stats,
        "stock_alerts": stock_alerts,
        "forecast": forecast,
        "suggestions": suggestions,
    }


def get_merchant_stats(merchant_id: str) -> Dict[str, Any]:
    """Get merchant's order and revenue stats."""
    orders_table = dynamodb.Table(ORDERS_TABLE)

    # Get yesterday's orders
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

    # Get today's orders
    today = datetime.now(timezone.utc)
    today_start = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    try:
        # Query yesterday's orders
        yesterday_response = orders_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("merchant_id").eq(merchant_id)
            & boto3.dynamodb.conditions.Attr("created_at").between(yesterday_start, yesterday_end)
        )
        yesterday_orders = yesterday_response.get("Items", [])

        # Query today's orders
        today_response = orders_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("merchant_id").eq(merchant_id)
            & boto3.dynamodb.conditions.Attr("created_at").gte(today_start)
        )
        today_orders = today_response.get("Items", [])

        # Calculate stats
        yesterday_count = len(yesterday_orders)
        yesterday_revenue = sum(int(o.get("total", 0)) for o in yesterday_orders)
        yesterday_commission_saved = sum(int(o.get("savings", 0)) for o in yesterday_orders)

        today_count = len(today_orders)
        today_revenue = sum(int(o.get("total", 0)) for o in today_orders)
        today_commission_saved = sum(int(o.get("savings", 0)) for o in today_orders)
        today_received = sum(int(o.get("total", 0)) - int(o.get("commission_ondc", 0)) for o in today_orders)

        return {
            "orders_today": today_count,
            "orders_yesterday": yesterday_count,
            "revenue_today": today_revenue,
            "revenue_yesterday": yesterday_revenue,
            "amount_received": today_received,
            "commission_saved": today_commission_saved,
        }
    except Exception as e:
        print(f"Error getting merchant stats: {e}")
        # Return mock data for demo
        return {
            "orders_today": 12,
            "orders_yesterday": 8,
            "revenue_today": 3200,
            "revenue_yesterday": 2400,
            "amount_received": 2950,
            "commission_saved": 640,
        }


def get_stock_alerts(merchant_id: str) -> List[Dict[str, Any]]:
    """Get low-stock product alerts.

    For demo purposes, returns mock alerts.
    In production, would query inventory management system.
    """
    # Mock stock alerts
    return [
        {
            "product": "Amul Gold Milk 500ml",
            "product_hi": "अमूल गोल्ड दूध 500ml",
            "severity": "high",
            "current_stock": 5,
            "message": "Only 5 units left",
        },
        {
            "product": "Tata Salt 1kg",
            "product_hi": "टाटा नमक 1kg",
            "severity": "medium",
            "current_stock": 15,
            "message": "Stock running low",
        },
        {
            "product": "Fortune Sunflower Oil 1L",
            "product_hi": "फॉर्च्यून सूरजमुखी तेल 1L",
            "severity": "high",
            "current_stock": 3,
            "message": "Urgent restock needed",
        },
    ]


def get_demand_forecast(merchant_id: str) -> Dict[str, Any]:
    """Get demand forecast based on upcoming events/festivals.

    For demo purposes, returns mock forecast.
    In production, would use ML model trained on historical data.
    """
    # Check upcoming festivals (hardcoded for demo)
    today = datetime.now(timezone.utc)

    # Holi example (March)
    if today.month == 3:
        return {
            "festival": "Holi",
            "festival_hi": "होली",
            "predicted_demand": "30% increase expected in colors, sweets, and snacks",
            "predicted_demand_hi": "रंग, मिठाई और नमकीन की मांग में 30% बढ़ोतरी",
            "date": "March 25",
            "suggested_stock_up": ["Colors", "Gujiyas", "Thandai", "Namkeen", "Sweets"],
        }

    # Diwali example (October/November)
    if today.month in [10, 11]:
        return {
            "festival": "Diwali",
            "festival_hi": "दिवाली",
            "predicted_demand": "50% increase expected in diyas, sweets, and dry fruits",
            "predicted_demand_hi": "दिए, मिठाई और ड्राई फ्रूट्स की मांग में 50% बढ़ोतरी",
            "date": "November 1",
            "suggested_stock_up": ["Diyas", "Sweets", "Dry Fruits", "Crackers", "Decorations"],
        }

    # Generic forecast
    return {
        "predicted_demand": "Weekend demand expected to be 20% higher than weekdays",
        "predicted_demand_hi": "सप्ताहांत में सप्ताह के दिनों की तुलना में 20% अधिक मांग",
        "suggested_stock_up": ["Milk", "Bread", "Eggs", "Vegetables"],
    }


def generate_suggestions(
    merchant_id: str, stats: Dict[str, Any], stock_alerts: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """Generate actionable suggestions for the merchant."""
    suggestions = []

    # Stock-based suggestions
    if stock_alerts and len(stock_alerts) > 0:
        suggestions.append({
            "text": f"Restock {len(stock_alerts)} low-stock products to avoid stockouts",
            "text_hi": f"{len(stock_alerts)} कम स्टॉक वाले उत्पादों को फिर से स्टॉक करें",
            "action": "restock",
        })

    # Order growth suggestions
    if stats["orders_today"] > stats["orders_yesterday"]:
        increase = stats["orders_today"] - stats["orders_yesterday"]
        suggestions.append({
            "text": f"Great! {increase} more orders than yesterday. Keep it up!",
            "text_hi": f"बढ़िया! कल से {increase} ऑर्डर ज्यादा। ऐसे ही चलते रहो!",
            "action": "celebrate",
        })
    else:
        suggestions.append({
            "text": "Share your ONDC store link on WhatsApp to get more orders",
            "text_hi": "ज्यादा ऑर्डर के लिए WhatsApp पे अपना ONDC स्टोर लिंक शेयर करें",
            "action": "share_link",
        })

    # Commission savings highlight
    if stats["commission_saved"] > 500:
        suggestions.append({
            "text": f"You saved ₹{stats['commission_saved']} in commissions today!",
            "text_hi": f"आज आपने ₹{stats['commission_saved']} कमीशन बचाया!",
            "action": "celebrate",
        })

    return suggestions
