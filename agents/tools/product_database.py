"""Product database — curated Indian FMCG products with images for text-based catalog creation."""

import json
import random
from strands import tool

# Common Indian FMCG products organized by category
# Image URLs use Open Food Facts / placeholder patterns
PRODUCT_DATABASE = {
    "Dairy": [
        {"name_en": "Amul Gold Milk 500ml", "name_hi": "अमूल गोल्ड दूध 500ml", "brand": "Amul", "price": 32, "variant": "500ml", "image_url": "https://m.media-amazon.com/images/I/71MXeEVDfPL._SL1500_.jpg"},
        {"name_en": "Amul Taaza Toned Milk 500ml", "name_hi": "अमूल ताज़ा टोन्ड दूध 500ml", "brand": "Amul", "price": 27, "variant": "500ml", "image_url": "https://m.media-amazon.com/images/I/41b1MFWxDOL.jpg"},
        {"name_en": "Mother Dairy Classic Curd 400g", "name_hi": "मदर डेयरी क्लासिक दही 400g", "brand": "Mother Dairy", "price": 35, "variant": "400g", "image_url": "https://m.media-amazon.com/images/I/51jz6CSYOAL._SL1000_.jpg"},
        {"name_en": "Amul Masti Buttermilk 200ml", "name_hi": "अमूल मस्ती छाछ 200ml", "brand": "Amul", "price": 15, "variant": "200ml", "image_url": "https://m.media-amazon.com/images/I/61DpLpBuYkL._SL1200_.jpg"},
        {"name_en": "Amul Butter 100g", "name_hi": "अमूल बटर 100g", "brand": "Amul", "price": 56, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/41MXbbuoSxL.jpg"},
        {"name_en": "Amul Fresh Paneer 200g", "name_hi": "अमूल फ्रेश पनीर 200g", "brand": "Amul", "price": 90, "variant": "200g", "image_url": "https://m.media-amazon.com/images/I/71gNueE3gcL._SL1500_.jpg"},
        {"name_en": "Amul Pure Ghee 500ml", "name_hi": "अमूल शुद्ध घी 500ml", "brand": "Amul", "price": 290, "variant": "500ml", "image_url": "https://m.media-amazon.com/images/I/51pBLOGhFHL._SL1000_.jpg"},
        {"name_en": "Mother Dairy Mishti Doi 100g", "name_hi": "मदर डेयरी मिष्टी दोई 100g", "brand": "Mother Dairy", "price": 25, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/71DsCUL5Y-L._SL1500_.jpg"},
        {"name_en": "Amul Cheese Slices 100g", "name_hi": "अमूल चीज़ स्लाइस 100g", "brand": "Amul", "price": 95, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/71XQMp2HXBL._SL1500_.jpg"},
        {"name_en": "Nestle Milkmaid 400g", "name_hi": "नेस्ले मिल्कमेड 400g", "brand": "Nestle", "price": 155, "variant": "400g", "image_url": "https://m.media-amazon.com/images/I/51Xm4WCuMeL._SL1000_.jpg"},
    ],
    "Staples": [
        {"name_en": "Aashirvaad Whole Wheat Atta 5kg", "name_hi": "आशीर्वाद आटा 5kg", "brand": "Aashirvaad", "price": 265, "variant": "5kg", "image_url": "https://m.media-amazon.com/images/I/71TaBqXaAKL._SL1500_.jpg"},
        {"name_en": "Fortune Sunlite Refined Oil 1L", "name_hi": "फॉर्च्यून सनलाइट रिफाइंड तेल 1L", "brand": "Fortune", "price": 140, "variant": "1L", "image_url": "https://m.media-amazon.com/images/I/61FRJxMb4hL._SL1000_.jpg"},
        {"name_en": "India Gate Basmati Rice 5kg", "name_hi": "इंडिया गेट बासमती चावल 5kg", "brand": "India Gate", "price": 450, "variant": "5kg", "image_url": "https://m.media-amazon.com/images/I/71FVIoIGRkL._SL1500_.jpg"},
        {"name_en": "Tata Salt 1kg", "name_hi": "टाटा नमक 1kg", "brand": "Tata", "price": 28, "variant": "1kg", "image_url": "https://m.media-amazon.com/images/I/61bkU82VQrL._SL1500_.jpg"},
        {"name_en": "Toor Dal 1kg", "name_hi": "तूर दाल 1kg", "brand": "Local", "price": 160, "variant": "1kg", "is_loose_item": True, "image_url": "https://m.media-amazon.com/images/I/71YvVWPgBtL._SL1500_.jpg"},
        {"name_en": "Sugar 1kg", "name_hi": "चीनी 1kg", "brand": "Local", "price": 45, "variant": "1kg", "is_loose_item": True, "image_url": "https://m.media-amazon.com/images/I/61RBx6QabHL._SL1500_.jpg"},
        {"name_en": "MDH Chana Masala 100g", "name_hi": "MDH चना मसाला 100g", "brand": "MDH", "price": 72, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/61UzaOlxI3L._SL1100_.jpg"},
        {"name_en": "Everest Garam Masala 100g", "name_hi": "एवरेस्ट गरम मसाला 100g", "brand": "Everest", "price": 96, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/61eWpaPGvVL._SL1200_.jpg"},
        {"name_en": "Rajma 1kg", "name_hi": "राजमा 1kg", "brand": "Local", "price": 140, "variant": "1kg", "is_loose_item": True, "image_url": "https://m.media-amazon.com/images/I/51LbIiEYQfL._SL1100_.jpg"},
        {"name_en": "Moong Dal 1kg", "name_hi": "मूंग दाल 1kg", "brand": "Local", "price": 130, "variant": "1kg", "is_loose_item": True, "image_url": "https://m.media-amazon.com/images/I/71fR-Sc0-DL._SL1500_.jpg"},
    ],
    "Snacks": [
        {"name_en": "Haldiram Aloo Bhujia 200g", "name_hi": "हल्दीराम आलू भुजिया 200g", "brand": "Haldiram", "price": 55, "variant": "200g", "image_url": "https://m.media-amazon.com/images/I/81E2fLbRecL._SL1500_.jpg"},
        {"name_en": "Lays Classic Salted 52g", "name_hi": "लेज़ क्लासिक नमकीन 52g", "brand": "Lays", "price": 20, "variant": "52g", "image_url": "https://m.media-amazon.com/images/I/81vJyb43URL._SL1500_.jpg"},
        {"name_en": "Kurkure Masala Munch 80g", "name_hi": "कुरकुरे मसाला मंच 80g", "brand": "Kurkure", "price": 20, "variant": "80g", "image_url": "https://m.media-amazon.com/images/I/81SAt7SgrSL._SL1500_.jpg"},
        {"name_en": "Parle-G Gold Biscuit 100g", "name_hi": "पारले-जी गोल्ड बिस्किट 100g", "brand": "Parle", "price": 25, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/81VUE1MkmuL._SL1500_.jpg"},
        {"name_en": "Britannia Good Day Butter 75g", "name_hi": "ब्रिटानिया गुड डे बटर 75g", "brand": "Britannia", "price": 30, "variant": "75g", "image_url": "https://m.media-amazon.com/images/I/91bZBb2RKVL._SL1500_.jpg"},
        {"name_en": "Bingo Mad Angles 72.5g", "name_hi": "बिंगो मैड एंगल्स 72.5g", "brand": "ITC", "price": 20, "variant": "72.5g", "image_url": "https://m.media-amazon.com/images/I/81rAlYN-EBL._SL1500_.jpg"},
        {"name_en": "Maggi 2-Minute Noodles 70g", "name_hi": "मैगी 2-मिनट नूडल्स 70g", "brand": "Nestle", "price": 14, "variant": "70g", "image_url": "https://m.media-amazon.com/images/I/81DyzPzmHTL._SL1500_.jpg"},
        {"name_en": "Haldiram Moong Dal 200g", "name_hi": "हल्दीराम मूंग दाल 200g", "brand": "Haldiram", "price": 50, "variant": "200g", "image_url": "https://m.media-amazon.com/images/I/81KcqQfHZDL._SL1500_.jpg"},
    ],
    "Beverages": [
        {"name_en": "Tata Tea Gold 500g", "name_hi": "टाटा टी गोल्ड 500g", "brand": "Tata", "price": 280, "variant": "500g", "image_url": "https://m.media-amazon.com/images/I/71v7xJw6bTL._SL1500_.jpg"},
        {"name_en": "Nescafe Classic Coffee 50g", "name_hi": "नेस्कैफे क्लासिक कॉफी 50g", "brand": "Nestle", "price": 155, "variant": "50g", "image_url": "https://m.media-amazon.com/images/I/61C8MYtgb5L._SL1500_.jpg"},
        {"name_en": "Coca-Cola 750ml", "name_hi": "कोका-कोला 750ml", "brand": "Coca-Cola", "price": 40, "variant": "750ml", "image_url": "https://m.media-amazon.com/images/I/51q1fgyCo8L._SL1500_.jpg"},
        {"name_en": "Thums Up 750ml", "name_hi": "थम्स अप 750ml", "brand": "Coca-Cola", "price": 40, "variant": "750ml", "image_url": "https://m.media-amazon.com/images/I/51xXR2zrBBL._SL1500_.jpg"},
        {"name_en": "Frooti Mango Drink 600ml", "name_hi": "फ्रूटी मैंगो ड्रिंक 600ml", "brand": "Parle Agro", "price": 30, "variant": "600ml", "image_url": "https://m.media-amazon.com/images/I/41R4g0x+Y7L._SL1000_.jpg"},
        {"name_en": "Real Fruit Juice Mixed Fruit 1L", "name_hi": "रियल फ्रूट जूस मिक्स्ड फ्रूट 1L", "brand": "Dabur", "price": 105, "variant": "1L", "image_url": "https://m.media-amazon.com/images/I/71bS3GU-g4L._SL1500_.jpg"},
        {"name_en": "Bisleri Water 1L", "name_hi": "बिसलेरी पानी 1L", "brand": "Bisleri", "price": 22, "variant": "1L", "image_url": "https://m.media-amazon.com/images/I/61ABnhHq-0L._SL1500_.jpg"},
    ],
    "Personal Care": [
        {"name_en": "Dove Beauty Bar 100g", "name_hi": "डव ब्यूटी बार 100g", "brand": "HUL", "price": 55, "variant": "100g", "image_url": "https://m.media-amazon.com/images/I/51+ysfSsimL._SL1100_.jpg"},
        {"name_en": "Colgate MaxFresh Toothpaste 150g", "name_hi": "कोलगेट मैक्सफ्रेश टूथपेस्ट 150g", "brand": "Colgate", "price": 95, "variant": "150g", "image_url": "https://m.media-amazon.com/images/I/61u3aCHPGWL._SL1000_.jpg"},
        {"name_en": "Head & Shoulders Shampoo 180ml", "name_hi": "हेड एंड शोल्डर्स शैम्पू 180ml", "brand": "P&G", "price": 190, "variant": "180ml", "image_url": "https://m.media-amazon.com/images/I/51MNJy-s4cL._SL1100_.jpg"},
        {"name_en": "Dettol Original Soap 125g", "name_hi": "डेटॉल ओरिजिनल साबुन 125g", "brand": "Reckitt", "price": 42, "variant": "125g", "image_url": "https://m.media-amazon.com/images/I/51h7vOYrR8L._SL1100_.jpg"},
        {"name_en": "Vaseline Body Lotion 200ml", "name_hi": "वैसलीन बॉडी लोशन 200ml", "brand": "HUL", "price": 165, "variant": "200ml", "image_url": "https://m.media-amazon.com/images/I/51Kv3JCwCpL._SL1100_.jpg"},
        {"name_en": "Nivea Men Deo 150ml", "name_hi": "निवेया मेन डियो 150ml", "brand": "Nivea", "price": 199, "variant": "150ml", "image_url": "https://m.media-amazon.com/images/I/51K-KJCkgyL._SL1200_.jpg"},
    ],
    "Household": [
        {"name_en": "Surf Excel Easy Wash 1kg", "name_hi": "सर्फ एक्सेल ईज़ी वॉश 1kg", "brand": "HUL", "price": 120, "variant": "1kg", "image_url": "https://m.media-amazon.com/images/I/61-t8fQ87bL._SL1000_.jpg"},
        {"name_en": "Vim Dishwash Bar 200g", "name_hi": "विम डिशवॉश बार 200g", "brand": "HUL", "price": 10, "variant": "200g", "image_url": "https://m.media-amazon.com/images/I/61OuePGHJxL._SL1500_.jpg"},
        {"name_en": "Lizol Floor Cleaner 500ml", "name_hi": "लाइज़ोल फ्लोर क्लीनर 500ml", "brand": "Reckitt", "price": 110, "variant": "500ml", "image_url": "https://m.media-amazon.com/images/I/61h-3zhYxvL._SL1500_.jpg"},
        {"name_en": "Good Knight Liquid Refill 45ml", "name_hi": "गुड नाइट लिक्विड रिफिल 45ml", "brand": "Godrej", "price": 49, "variant": "45ml", "image_url": "https://m.media-amazon.com/images/I/51KuN33c-EL._SL1500_.jpg"},
        {"name_en": "Harpic Power Plus 500ml", "name_hi": "हार्पिक पावर प्लस 500ml", "brand": "Reckitt", "price": 85, "variant": "500ml", "image_url": "https://m.media-amazon.com/images/I/61MN5RM3qKL._SL1000_.jpg"},
    ],
}

# Category keyword mapping for fuzzy matching
CATEGORY_KEYWORDS = {
    "Dairy": ["dairy", "milk", "doodh", "दूध", "dahi", "दही", "curd", "paneer", "पनीर", "butter", "मक्खन", "ghee", "घी", "cheese", "चीज़", "cream"],
    "Staples": ["staples", "atta", "आटा", "rice", "chawal", "चावल", "dal", "दाल", "oil", "तेल", "salt", "नमक", "sugar", "चीनी", "masala", "मसाला", "spice", "rajma", "moong"],
    "Snacks": ["snacks", "namkeen", "नमकीन", "chips", "biscuit", "बिस्किट", "bhujia", "भुजिया", "noodles", "maggi", "मैगी", "kurkure", "lays"],
    "Beverages": ["beverages", "tea", "chai", "चाय", "coffee", "कॉफी", "cold drink", "juice", "जूस", "water", "पानी", "cola", "soda", "drink"],
    "Personal Care": ["personal care", "soap", "साबुन", "shampoo", "शैम्पू", "toothpaste", "टूथपेस्ट", "cream", "deo", "lotion"],
    "Household": ["household", "detergent", "dishwash", "floor cleaner", "phenyl", "mosquito", "harpic", "surf", "vim"],
}


def _match_categories(description: str) -> list[str]:
    """Match a text description to product categories."""
    desc_lower = description.lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if category not in matched:
                    matched.append(category)
                break
    # If nothing matched, return top categories for a general store
    if not matched:
        matched = ["Dairy", "Staples", "Snacks", "Beverages"]
    return matched


@tool
def suggest_products_from_description(description: str, max_per_category: str = "5") -> str:
    """Suggest products with images based on a text description of what the store sells.
    Use this when a merchant describes their products verbally instead of sending photos.

    Args:
        description: What the merchant says they sell, e.g. "dairy products like milk, dahi, ghee" or "general kirana store items"
        max_per_category: Maximum products to suggest per category (default "5")

    Returns:
        JSON with suggested products organized by category, each with name, price, and image_url
    """
    max_n = int(max_per_category)
    categories = _match_categories(description)

    suggestions = {}
    total = 0
    for cat in categories:
        products = PRODUCT_DATABASE.get(cat, [])
        # Pick up to max_n products per category
        selected = products[:max_n]
        suggestions[cat] = selected
        total += len(selected)

    return json.dumps({
        "status": "success",
        "description": description,
        "categories_matched": categories,
        "total_products": total,
        "products_by_category": suggestions,
        "message": f"Found {total} products across {len(categories)} categories. Show these to the merchant and ask for confirmation before saving.",
    }, ensure_ascii=False)


@tool
def get_product_suggestions_for_category(category: str) -> str:
    """Get all available product suggestions for a specific category.

    Args:
        category: Category name — one of: Dairy, Staples, Snacks, Beverages, Personal Care, Household

    Returns:
        JSON with all products in that category with names, prices, and image URLs
    """
    products = PRODUCT_DATABASE.get(category, [])
    if not products:
        # Try case-insensitive match
        for cat, prods in PRODUCT_DATABASE.items():
            if cat.lower() == category.lower():
                products = prods
                break

    return json.dumps({
        "category": category,
        "total_products": len(products),
        "products": products,
    }, ensure_ascii=False)
