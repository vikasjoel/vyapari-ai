"""Onboarding Agent — handles merchant registration via Hindi conversation with dynamic slot-filling."""

from strands import Agent
from strands.models.bedrock import BedrockModel
from agents.prompts.onboarding_prompt import ONBOARDING_SYSTEM_PROMPT
from agents.tools.dynamodb_tools import save_merchant, check_duplicate, get_merchant, update_merchant

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_onboarding_agent() -> Agent:
    """Create the onboarding agent with DynamoDB tools."""
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    agent = Agent(
        model=model,
        system_prompt=ONBOARDING_SYSTEM_PROMPT,
        tools=[save_merchant, check_duplicate, get_merchant, update_merchant],
    )

    return agent
