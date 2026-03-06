"""Invoice extraction tools — Claude multimodal analysis of purchase invoices."""

import json
import base64
import os

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
S3_PHOTOS_BUCKET = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")

s3_client = boto3.client("s3", region_name=REGION)
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)

INVOICE_EXTRACTION_PROMPT = """Analyze this purchase invoice image from an Indian merchant/distributor.

Extract ALL product line items from the invoice. For each product, extract:
- product_name: Full product name as written on invoice
- brand: Brand name if visible
- quantity: Number of units purchased
- unit_price: Price per unit in INR
- total_price: Total price for this line item in INR
- hsn_code: HSN code if visible on invoice

Also extract:
- invoice_number: Invoice/bill number
- invoice_date: Date on invoice
- supplier_name: Supplier/distributor name
- total_amount: Grand total amount

Return a JSON object with this structure:
{
  "invoice_number": "...",
  "invoice_date": "...",
  "supplier_name": "...",
  "products": [
    {"product_name": "...", "brand": "...", "quantity": N, "unit_price": N, "total_price": N, "hsn_code": "..."},
    ...
  ],
  "total_amount": N
}

IMPORTANT:
- Extract ALL products, even if partially visible
- Prices must be in INR (Indian Rupees)
- If HSN code is not visible, leave it as empty string
- If brand is not clear, leave as empty string
- Return ONLY the JSON, no other text"""


@tool
def extract_invoice(invoice_s3_key: str) -> str:
    """Extract product details from a purchase invoice photo using Claude multimodal.

    Analyzes the invoice image to extract product names, quantities, prices,
    and supplier information. Use this when a merchant uploads a distributor
    invoice to quickly add products to their catalog.

    Args:
        invoice_s3_key: S3 key of the uploaded invoice image (in the photos bucket)

    Returns:
        JSON with extracted invoice details including products list, supplier info, and totals
    """
    # Fetch image from S3
    try:
        response = s3_client.get_object(Bucket=S3_PHOTOS_BUCKET, Key=invoice_s3_key)
        image_bytes = response["Body"].read()
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Could not fetch invoice from S3: {str(e)}",
        }, ensure_ascii=False)

    # Determine media type
    key_lower = invoice_s3_key.lower()
    if key_lower.endswith(".png"):
        media_type = "image/png"
    elif key_lower.endswith(".webp"):
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"

    # Call Bedrock Claude multimodal
    try:
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
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            },
                        },
                        {
                            "type": "text",
                            "text": INVOICE_EXTRACTION_PROMPT,
                        },
                    ],
                }
            ],
        })

        response = bedrock_client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        result = json.loads(response["body"].read().decode("utf-8"))
        content_text = result["content"][0]["text"]

        # Parse the JSON from Claude's response
        # Strip markdown code fences if present
        clean_text = content_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

        invoice_data = json.loads(clean_text)

        return json.dumps({
            "status": "success",
            "source": "invoice_extraction",
            "invoice": invoice_data,
            "products_found": len(invoice_data.get("products", [])),
            "message": f"Extracted {len(invoice_data.get('products', []))} products from invoice",
        }, ensure_ascii=False)

    except json.JSONDecodeError:
        return json.dumps({
            "status": "partial",
            "message": "Invoice analyzed but could not parse structured data. Raw text extracted.",
            "raw_text": content_text[:500] if "content_text" in dir() else "No text extracted",
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Invoice analysis failed: {str(e)}",
        }, ensure_ascii=False)
