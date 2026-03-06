"""Catalog Agent — template-first catalog creation with photo, text, barcode, and invoice paths."""

from strands import Agent
from strands.models.bedrock import BedrockModel
from agents.prompts.catalog_prompt import CATALOG_SYSTEM_PROMPT
from agents.tools.bedrock_tools import analyze_photo, analyze_photo_from_s3
from agents.tools.s3_tools import upload_photo, get_photo_url
from agents.tools.ondc_tools import save_catalog, get_catalog, update_product, generate_beckn_schema
from agents.tools.seed_db_tools import load_template, search_seed_db, get_categories
from agents.tools.barcode_tools import lookup_barcode
from agents.tools.invoice_tools import extract_invoice

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_catalog_agent() -> Agent:
    """Create the catalog agent with template, photo, barcode, and invoice tools."""
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    agent = Agent(
        model=model,
        system_prompt=CATALOG_SYSTEM_PROMPT,
        tools=[
            # Template tools (primary)
            load_template,
            search_seed_db,
            get_categories,
            # Photo tools (secondary)
            analyze_photo,
            analyze_photo_from_s3,
            upload_photo,
            get_photo_url,
            # Barcode tool
            lookup_barcode,
            # Invoice tool
            extract_invoice,
            # Catalog management
            save_catalog,
            get_catalog,
            update_product,
            generate_beckn_schema,
        ],
    )

    return agent
