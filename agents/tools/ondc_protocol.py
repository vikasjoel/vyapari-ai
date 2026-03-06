"""ONDC Protocol module — domain mapping, fee calculations, logistics simulation."""

import random

# ── Store type → ONDC Domain mapping ──
STORE_TYPE_TO_ONDC_DOMAIN = {
    "kirana": {"domain": "ONDC:RET10", "label": "Grocery"},
    "restaurant": {"domain": "ONDC:RET11", "label": "F&B"},
    "sweet_shop": {"domain": "ONDC:RET11", "label": "F&B"},
    "bakery": {"domain": "ONDC:RET11", "label": "F&B"},
}

# ── ONDC Buyer Apps with finder fees ──
ONDC_BUYER_APPS = [
    {"name": "Paytm", "finder_fee_pct": 3.0, "icon": "paytm"},
    {"name": "Magicpin", "finder_fee_pct": 2.5, "icon": "magicpin"},
    {"name": "Ola", "finder_fee_pct": 3.5, "icon": "ola"},
    {"name": "myStore", "finder_fee_pct": 2.0, "icon": "mystore"},
    {"name": "ONDC Reference App", "finder_fee_pct": 0.0, "icon": "ondc"},
]

BUYER_APP_NAMES = [app["name"] for app in ONDC_BUYER_APPS]

# ── Logistics Partners ──
LOGISTICS_PARTNERS = [
    {"name": "Shadowfax", "base_charge": 25, "per_km": 8, "eta_min": 25, "eta_max": 40},
    {"name": "Dunzo", "base_charge": 30, "per_km": 10, "eta_min": 20, "eta_max": 35},
    {"name": "Borzo", "base_charge": 20, "per_km": 7, "eta_min": 30, "eta_max": 50},
    {"name": "Porter", "base_charge": 35, "per_km": 9, "eta_min": 20, "eta_max": 30},
]

# ── Common Indian rider names for simulation ──
RIDER_NAMES = [
    "Raju", "Suresh", "Manoj", "Deepak", "Vikram", "Sanjay", "Amit",
    "Rahul", "Ajay", "Kiran", "Mohan", "Pradeep", "Santosh", "Rajesh",
    "Govind", "Ashok", "Naveen", "Ramesh", "Prakash", "Dinesh",
]

# ── ONDC Network & Seller App fixed rates ──
ONDC_NETWORK_FEE_PCT = 0.5   # ONDC network fee (% of order total)
SELLER_APP_FEE_PCT = 1.5     # Vyapari.ai seller app fee (% of order total)
GST_RATE = 0.18              # 18% GST on fees

# ── Aggregator commission rates ──
AGGREGATOR_RATES = {
    "Swiggy": {"min": 25, "max": 35},
    "Zomato": {"min": 22, "max": 30},
    "Blinkit": {"min": 20, "max": 28},
}


def get_buyer_app(name: str) -> dict | None:
    """Get buyer app details by name."""
    for app in ONDC_BUYER_APPS:
        if app["name"].lower() == name.lower():
            return app
    return None


def get_ondc_domain(store_type: str) -> dict:
    """Get ONDC domain code and label for a store type."""
    return STORE_TYPE_TO_ONDC_DOMAIN.get(
        store_type.lower(),
        {"domain": "ONDC:RET10", "label": "Grocery"},
    )


def calculate_ondc_fees(
    order_total: float,
    buyer_app: str,
    logistics_distance_km: float = 3.0,
) -> dict:
    """Calculate detailed ONDC fee breakdown for an order.

    Returns:
        Dict with buyer_app_finder_fee, seller_app_fee, ondc_network_fee,
        logistics_cost, logistics_partner, logistics_eta, logistics_rider,
        gst_on_fees, total_deductions, merchant_receives.
    """
    # Buyer app finder fee
    app = get_buyer_app(buyer_app)
    finder_fee_pct = app["finder_fee_pct"] if app else 3.0
    buyer_app_finder_fee = round(order_total * finder_fee_pct / 100, 2)

    # Seller app fee (Vyapari.ai)
    seller_app_fee = round(order_total * SELLER_APP_FEE_PCT / 100, 2)

    # ONDC network fee
    ondc_network_fee = round(order_total * ONDC_NETWORK_FEE_PCT / 100, 2)

    # Logistics
    partner = random.choice(LOGISTICS_PARTNERS)
    logistics_cost = round(partner["base_charge"] + partner["per_km"] * logistics_distance_km, 2)
    logistics_eta = random.randint(partner["eta_min"], partner["eta_max"])
    logistics_rider = random.choice(RIDER_NAMES)

    # GST on platform fees (not on logistics)
    platform_fees = buyer_app_finder_fee + seller_app_fee + ondc_network_fee
    gst_on_fees = round(platform_fees * GST_RATE, 2)

    # Total deductions
    total_deductions = round(
        buyer_app_finder_fee + seller_app_fee + ondc_network_fee + logistics_cost + gst_on_fees,
        2,
    )
    merchant_receives = round(order_total - total_deductions, 2)

    # Also compute the combined "commission" for backward compat
    commission_ondc = round(buyer_app_finder_fee + seller_app_fee + ondc_network_fee + gst_on_fees, 2)

    return {
        "buyer_app": buyer_app,
        "buyer_app_finder_fee": buyer_app_finder_fee,
        "buyer_app_finder_fee_pct": finder_fee_pct,
        "seller_app_fee": seller_app_fee,
        "seller_app_fee_pct": SELLER_APP_FEE_PCT,
        "ondc_network_fee": ondc_network_fee,
        "ondc_network_fee_pct": ONDC_NETWORK_FEE_PCT,
        "logistics_cost": logistics_cost,
        "logistics_partner": partner["name"],
        "logistics_eta": logistics_eta,
        "logistics_rider": logistics_rider,
        "logistics_distance_km": logistics_distance_km,
        "gst_on_fees": gst_on_fees,
        "total_deductions": total_deductions,
        "merchant_receives": merchant_receives,
        "commission_ondc": commission_ondc,
    }


def calculate_aggregator_fees(order_total: float, platform: str = "Swiggy") -> dict:
    """Calculate aggregator fees (Swiggy/Zomato/Blinkit) for comparison.

    Returns:
        Dict with commission, gst, total_deductions, merchant_receives.
    """
    rates = AGGREGATOR_RATES.get(platform, AGGREGATOR_RATES["Swiggy"])
    rate = random.uniform(rates["min"], rates["max"])
    commission = round(order_total * rate / 100, 2)
    gst = round(commission * GST_RATE, 2)
    total_deductions = round(commission + gst, 2)
    merchant_receives = round(order_total - total_deductions, 2)

    return {
        "platform": platform,
        "commission": commission,
        "commission_pct": round(rate, 1),
        "gst": gst,
        "total_deductions": total_deductions,
        "merchant_receives": merchant_receives,
    }
