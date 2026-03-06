"""DynamoDB tools for merchant, product, and order CRUD operations."""

import json
import uuid
import os
from datetime import datetime, timezone
from typing import Optional

import boto3
from dotenv import load_dotenv
from strands import tool

from agents.tools.ondc_protocol import (
    get_ondc_domain,
    ONDC_BUYER_APPS,
)

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
PRODUCTS_TABLE = os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products")
ORDERS_TABLE = os.getenv("DYNAMODB_ORDERS_TABLE", "vyapari-orders")
SESSIONS_TABLE = os.getenv("DYNAMODB_SESSIONS_TABLE", "vyapari-sessions")

dynamodb = boto3.resource("dynamodb", region_name=REGION)


@tool
def save_merchant(
    name: str,
    shop_name: str,
    shop_type: str,
    city: str,
    phone: str,
    street: str = "",
    area: str = "",
    state: str = "",
    pincode: str = "",
    operating_hours: str = "9:00 AM - 9:00 PM",
    serviceability_radius: str = "3",
    fssai_license: str = "",
    gst_number: str = "",
    payment_modes: str = "cash,upi",
    fulfillment_type: str = "delivery,pickup",
    cancellation_policy: str = "",
    return_policy: str = "",
) -> str:
    """Save a new merchant to DynamoDB after onboarding is complete.

    Args:
        name: Merchant's full name (e.g., "Ramesh Kumar")
        shop_name: Business name (e.g., "Ramesh Kirana Store")
        shop_type: Type of shop — one of: kirana, restaurant, sweet_shop, bakery
        city: City name (e.g., "Delhi", "Bangalore")
        phone: 10-digit Indian mobile number
        street: Street address / colony (e.g., "45, Main Market, Lajpat Nagar")
        area: Area/locality within the city (e.g., "Lajpat Nagar")
        state: State name (e.g., "Delhi", "Karnataka")
        pincode: 6-digit pincode
        operating_hours: Shop operating hours (e.g., "9:00 AM - 9:00 PM")
        serviceability_radius: Delivery radius in km (e.g., "3")
        fssai_license: FSSAI license number (required for restaurant, sweet_shop, bakery)
        gst_number: GST registration number (optional for all)
        payment_modes: Comma-separated payment modes (e.g., "cash,upi")
        fulfillment_type: Comma-separated fulfillment types (e.g., "delivery,pickup")
        cancellation_policy: Cancellation policy text (auto-filled based on shop_type if empty)
        return_policy: Return policy text (auto-filled based on shop_type if empty)

    Returns:
        JSON string with merchant_id, ONDC domain info, and success status
    """
    table = dynamodb.Table(MERCHANTS_TABLE)
    merchant_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Normalize phone: strip +91, spaces, hyphens
    clean_phone = phone.replace("+91", "").replace("-", "").replace(" ", "").strip()
    if len(clean_phone) > 10:
        clean_phone = clean_phone[-10:]

    # Get ONDC domain for this store type
    shop_type_lower = shop_type.lower()
    ondc_domain_info = get_ondc_domain(shop_type_lower)
    ondc_seller_id = f"ONDC-{merchant_id[:8].upper()}"

    # Buyer apps this merchant will be discoverable on
    discoverable_on = [app["name"] for app in ONDC_BUYER_APPS]

    # Smart defaults for policies based on store type
    if not cancellation_policy:
        if shop_type_lower == "kirana":
            cancellation_policy = "Order cancel within 5 minutes of placement"
        else:
            cancellation_policy = "Order cancel before preparation starts"

    if not return_policy:
        if shop_type_lower == "kirana":
            return_policy = "Return within 24 hours if damaged/wrong item"
        else:
            return_policy = "No returns on prepared food items"

    item = {
        "merchant_id": merchant_id,
        "phone": clean_phone,
        "name": name,
        "shop_name": shop_name,
        "shop_type": shop_type_lower,
        "location": {
            "street": street,
            "city": city,
            "area": area,
            "state": state,
            "pincode": pincode,
        },
        "ondc_seller_id": ondc_seller_id,
        "ondc_domain": ondc_domain_info["domain"],
        "ondc_domain_label": ondc_domain_info["label"],
        "onboarding_status": "registered",
        "languages": ["hi", "en"],
        "operating_hours": operating_hours,
        "serviceability_radius": serviceability_radius,
        "fulfillment_types": [f.strip() for f in fulfillment_type.split(",") if f.strip()],
        "payment_modes": [m.strip() for m in payment_modes.split(",") if m.strip()],
        "cancellation_policy": cancellation_policy,
        "return_policy": return_policy,
        "discoverable_on": discoverable_on,
        "created_at": now,
        "updated_at": now,
    }

    if fssai_license:
        item["fssai_license"] = fssai_license
    if gst_number:
        item["gst_number"] = gst_number

    table.put_item(Item=item)

    return json.dumps({
        "status": "success",
        "merchant_id": merchant_id,
        "shop_name": shop_name,
        "ondc_seller_id": ondc_seller_id,
        "ondc_domain": ondc_domain_info["domain"],
        "ondc_domain_label": ondc_domain_info["label"],
        "serviceability_radius": serviceability_radius,
        "operating_hours": operating_hours,
        "discoverable_on": discoverable_on,
        "fulfillment_types": [f.strip() for f in fulfillment_type.split(",") if f.strip()],
        "payment_modes": [m.strip() for m in payment_modes.split(",") if m.strip()],
    }, ensure_ascii=False)


@tool
def check_duplicate(phone: str) -> str:
    """Check if a merchant with this phone number already exists.

    Args:
        phone: 10-digit Indian mobile number to check

    Returns:
        JSON string with exists=true/false and merchant data if found
    """
    table = dynamodb.Table(MERCHANTS_TABLE)

    clean_phone = phone.replace("+91", "").replace("-", "").replace(" ", "").strip()
    if len(clean_phone) > 10:
        clean_phone = clean_phone[-10:]

    response = table.query(
        IndexName="phone-index",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("phone").eq(clean_phone),
    )

    items = response.get("Items", [])
    if items:
        merchant = items[0]
        return (
            f'{{"exists": true, "merchant_id": "{merchant["merchant_id"]}", '
            f'"name": "{merchant["name"]}", "shop_name": "{merchant["shop_name"]}"}}'
        )

    return '{"exists": false}'


@tool
def get_merchant(merchant_id: str) -> str:
    """Retrieve a merchant's details by their merchant_id.

    Args:
        merchant_id: The unique merchant identifier (UUID)

    Returns:
        JSON string with merchant details or not_found status
    """
    table = dynamodb.Table(MERCHANTS_TABLE)

    response = table.get_item(Key={"merchant_id": merchant_id})
    item = response.get("Item")

    if not item:
        return f'{{"status": "not_found", "merchant_id": "{merchant_id}"}}'

    location = item.get("location", {})
    return (
        f'{{"status": "found", "merchant_id": "{item["merchant_id"]}", '
        f'"name": "{item["name"]}", "shop_name": "{item["shop_name"]}", '
        f'"shop_type": "{item["shop_type"]}", '
        f'"city": "{location.get("city", "")}", "area": "{location.get("area", "")}", '
        f'"phone": "{item["phone"]}", '
        f'"onboarding_status": "{item["onboarding_status"]}"}}'
    )


@tool
def update_merchant(merchant_id: str, updates: str) -> str:
    """Update a merchant's details. Pass updates as key=value pairs separated by commas.

    Args:
        merchant_id: The unique merchant identifier (UUID)
        updates: Comma-separated key=value pairs, e.g. "shop_name=New Name,phone=9876543210"

    Returns:
        JSON string with update status
    """
    table = dynamodb.Table(MERCHANTS_TABLE)
    now = datetime.now(timezone.utc).isoformat()

    # Parse updates string
    update_dict = {}
    for pair in updates.split(","):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            update_dict[key.strip()] = value.strip()

    if not update_dict:
        return '{"status": "error", "message": "No valid updates provided"}'

    # Build update expression
    expr_parts = ["#updated_at = :updated_at"]
    expr_names = {"#updated_at": "updated_at"}
    expr_values = {":updated_at": now}

    for i, (key, value) in enumerate(update_dict.items()):
        placeholder = f"#field{i}"
        value_placeholder = f":val{i}"
        expr_parts.append(f"{placeholder} = {value_placeholder}")
        expr_names[placeholder] = key
        expr_values[value_placeholder] = value

    table.update_item(
        Key={"merchant_id": merchant_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )

    return f'{{"status": "updated", "merchant_id": "{merchant_id}", "fields_updated": {list(update_dict.keys())}}}'
