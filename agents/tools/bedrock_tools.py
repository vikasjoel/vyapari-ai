"""Bedrock tools — multimodal photo analysis and KB search."""

import json
import base64
import os

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

bedrock_runtime = boto3.client("bedrock-runtime", region_name=REGION)

PHOTO_ANALYSIS_PROMPT = """You are an expert at identifying Indian FMCG products from shelf photos in kirana stores.

Analyze this photo and identify ALL visible products. For each product, provide:
- name_en: English product name with brand, variant, and size (e.g., "Amul Gold Milk 500ml")
- name_hi: Hindi name in Devanagari (e.g., "अमूल गोल्ड दूध 500ml")
- brand: Brand name (e.g., "Amul")
- variant: Size/weight/flavor (e.g., "500ml", "200g", "Masala")
- price: MRP in INR (integer). Use standard Indian retail prices. If price label visible, use that.
- category: One of: Grocery & Staples, Dairy, Snacks & Namkeen, Beverages, Personal Care, Household, Packaged Foods, Baby Care, Health & Hygiene, Confectionery
- description_hi: Short Hindi description (1 line)
- is_loose_item: true if sold by weight (dal, rice, etc.), false for packaged items
- confidence: 0.0 to 1.0 — how confident you are in the identification

IMPORTANT:
- Only include products you can actually see in the photo
- Use realistic Indian MRP prices (not US prices)
- Include ALL visible products, even partially visible ones (with lower confidence)
- Common Indian brands: Amul, Haldiram, Parle, Britannia, ITC (Aashirvaad, Sunfeast, Bingo), Dabur, Patanjali, HUL (Surf, Vim, Dove), Tata (Salt, Tea), MDH, Everest, Fortune, Maggi/Nestle

Return a JSON array of products. ONLY return the JSON array, no other text.

Example output:
[
  {"name_en": "Amul Gold Milk 500ml", "name_hi": "अमूल गोल्ड दूध 500ml", "brand": "Amul", "variant": "500ml", "price": 32, "category": "Dairy", "description_hi": "फुल क्रीम दूध", "is_loose_item": false, "confidence": 0.95},
  {"name_en": "Haldiram Aloo Bhujia 200g", "name_hi": "हल्दीराम आलू भुजिया 200g", "brand": "Haldiram", "variant": "200g", "price": 45, "category": "Snacks & Namkeen", "description_hi": "नमकीन आलू भुजिया", "is_loose_item": false, "confidence": 0.92}
]"""


@tool
def analyze_photo(photo_base64: str, media_type: str = "image/jpeg") -> str:
    """Analyze a shelf photo using Claude Sonnet 4 multimodal to identify products.

    Args:
        photo_base64: Base64-encoded image data
        media_type: MIME type of the image (image/jpeg, image/png, image/webp)

    Returns:
        JSON string with array of identified products
    """
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": photo_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": PHOTO_ANALYSIS_PROMPT,
                    },
                ],
            }
        ],
    })

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    result = json.loads(response["body"].read())
    text = result["content"][0]["text"]

    # Extract JSON from response (Claude sometimes wraps in markdown)
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Validate it's valid JSON
    try:
        products = json.loads(text)
        return json.dumps({"status": "success", "products": products, "count": len(products)})
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Could not parse product list from photo", "raw": text[:500]})


@tool
def analyze_photo_from_s3(s3_key: str, bucket: str = "") -> str:
    """Analyze a photo stored in S3 by downloading it and running multimodal analysis.

    Args:
        s3_key: The S3 object key for the photo
        bucket: S3 bucket name (defaults to photos bucket from env)

    Returns:
        JSON string with array of identified products
    """
    if not bucket:
        bucket = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")

    s3 = boto3.client("s3", region_name=REGION)
    response = s3.get_object(Bucket=bucket, Key=s3_key)
    image_bytes = response["Body"].read()
    photo_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # Detect media type from extension
    ext = s3_key.rsplit(".", 1)[-1].lower() if "." in s3_key else "jpg"
    media_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    media_type = media_types.get(ext, "image/jpeg")

    return analyze_photo(photo_base64=photo_base64, media_type=media_type)
