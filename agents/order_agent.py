"""Order Agent — ONDC order management, commission savings, fulfillment tracking."""

from strands import Agent
from strands.models.bedrock import BedrockModel
from agents.prompts.order_prompt import ORDER_SYSTEM_PROMPT
from agents.tools.order_tools import (
    create_order,
    get_orders,
    update_order_status,
    calculate_savings,
    simulate_order,
    select_logistics_partner,
)

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_order_agent() -> Agent:
    """Create the order agent with order management tools."""
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    agent = Agent(
        model=model,
        system_prompt=ORDER_SYSTEM_PROMPT,
        tools=[
            create_order,
            get_orders,
            update_order_status,
            calculate_savings,
            simulate_order,
            select_logistics_partner,
        ],
    )

    return agent
