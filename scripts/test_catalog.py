"""Test the catalog agent — photo analysis and catalog creation."""

import sys
import json
import base64
sys.path.insert(0, ".")

import boto3
import os
from dotenv import load_dotenv
load_dotenv()

from agents.catalog_agent import create_catalog_agent
from agents.tools.bedrock_tools import analyze_photo


def test_photo_analysis_direct():
    """Test direct photo analysis tool with Claude multimodal."""
    print("=== Test 1: Direct Photo Analysis (Tool) ===\n")

    with open("tests/fixtures/sample_shelf_photos/snacks_shelf.jpg", "rb") as f:
        photo_bytes = f.read()

    photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
    print(f"Photo size: {len(photo_bytes)} bytes")
    print("Calling analyze_photo...")

    result = analyze_photo(photo_base64=photo_base64, media_type="image/jpeg")
    data = json.loads(result)

    if data.get("status") == "success":
        print(f"\n✅ Products found: {data['count']}")
        for p in data["products"]:
            conf = p.get("confidence", "?")
            flag = " ⚠️" if isinstance(conf, (int, float)) and conf < 0.7 else ""
            print(f"  • {p.get('name_en', 'unknown')} — ₹{p.get('price', '?')} ({p.get('category', '?')}) [conf: {conf}]{flag}")
    else:
        print(f"❌ Error: {data}")

    return data


def test_catalog_agent_s3_flow():
    """Test catalog agent with S3-based photo flow (production path)."""
    print("\n=== Test 2: Catalog Agent via S3 ===\n")

    # Upload photo to S3 first
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))
    bucket = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")
    s3_key = "test/sample_shelf.jpg"

    with open("tests/fixtures/sample_shelf_photos/snacks_shelf.jpg", "rb") as f:
        s3.put_object(Bucket=bucket, Key=s3_key, Body=f.read(), ContentType="image/jpeg")
    print(f"Uploaded photo to s3://{bucket}/{s3_key}")

    # Now test catalog agent with S3 reference
    agent = create_catalog_agent()

    print("Sending S3 photo reference to catalog agent...\n")
    result = agent(
        f"Meri dukaan ki shelf photo hai. Please analyze it using analyze_photo_from_s3. "
        f"The S3 key is: {s3_key} and bucket is: {bucket}"
    )

    print(f"Agent response:\n{result.message}\n")

    # Cleanup S3
    s3.delete_object(Bucket=bucket, Key=s3_key)
    print("Cleaned up test photo from S3")

    return result


def test_save_catalog():
    """Test saving catalog to DynamoDB."""
    print("\n=== Test 3: Save Catalog to DynamoDB ===\n")

    from agents.tools.ondc_tools import save_catalog, get_catalog

    test_merchant_id = "test-merchant-catalog-001"
    products = [
        {"name_en": "Amul Gold Milk 500ml", "name_hi": "अमूल गोल्ड दूध", "brand": "Amul", "variant": "500ml", "price": 32, "category": "Dairy", "description_hi": "फुल क्रीम दूध", "is_loose_item": False, "confidence": 0.95},
        {"name_en": "Parle-G Biscuits 200g", "name_hi": "पारले-जी बिस्कुट", "brand": "Parle", "variant": "200g", "price": 20, "category": "Confectionery", "description_hi": "ग्लूकोज़ बिस्कुट", "is_loose_item": False, "confidence": 0.92},
    ]

    result = save_catalog(merchant_id=test_merchant_id, products_json=json.dumps(products))
    data = json.loads(result)
    print(f"Save result: {data}")

    # Verify
    catalog_result = get_catalog(merchant_id=test_merchant_id)
    catalog_data = json.loads(catalog_result)
    print(f"Catalog: {catalog_data['total_products']} products in {len(catalog_data['categories'])} categories")

    # Cleanup
    ddb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = ddb.Table(os.getenv("DYNAMODB_PRODUCTS_TABLE", "vyapari-products"))
    for pid in data.get("product_ids", []):
        table.delete_item(Key={"product_id": pid})
    print(f"Cleaned up {len(data.get('product_ids', []))} test products")


if __name__ == "__main__":
    test_photo_analysis_direct()
    test_save_catalog()
    test_catalog_agent_s3_flow()
    print("\n=== All Catalog Tests Complete ===")
