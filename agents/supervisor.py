"""Supervisor Agent — routes conversations to specialist agents.

Uses Strands multi-agent pattern: sub-agents are registered as tools.
Each call to create_supervisor_agent() creates FRESH sub-agents — no shared state between sessions.
"""

from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from agents.prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT
from agents.onboarding_agent import create_onboarding_agent
from agents.catalog_agent import create_catalog_agent
from agents.voice_agent import create_voice_agent
from agents.order_agent import create_order_agent
from agents.intelligence_agent import create_intelligence_agent

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_supervisor_agent() -> Agent:
    """Create the supervisor agent with FRESH sub-agent instances (per session)."""
    # Each session gets its own sub-agents — no context bleed
    onboarding_agent = create_onboarding_agent()
    catalog_agent = create_catalog_agent()
    voice_agent = create_voice_agent()
    order_agent = create_order_agent()
    intelligence_agent = create_intelligence_agent()

    @tool
    def handle_onboarding(message: str) -> str:
        """Route message to the onboarding specialist for merchant registration.
        Use this when:
        - A new merchant starts a conversation (greeting, introduction)
        - Merchant hasn't completed registration yet (missing name, shop name, shop type, location, or phone)
        - Merchant provides registration details (name, shop info, location, phone number)
        - Merchant wants to update their registration info
        - Merchant replies with short answers (yes/no/skip/numbers) during an ongoing registration flow

        Args:
            message: The merchant's message to process for onboarding

        Returns:
            The onboarding specialist's response to the merchant
        """
        result = onboarding_agent(message)
        return result.message

    @tool
    def handle_catalog(message: str) -> str:
        """Route message to the catalog specialist for product management.
        Use this when:
        - Merchant sends a photo of their shop shelf or products
        - Merchant asks about their product catalog or product list
        - Merchant wants to update a product price or mark something out of stock
        - Merchant asks to add or remove products
        - Merchant asks about ONDC catalog or publishing
        - Message contains photo/image data (base64 or S3 reference)
        - Merchant mentions "template", "catalog banao", "products select karo"

        Args:
            message: The merchant's message about catalog/products. May include base64 photo data or S3 key.

        Returns:
            The catalog specialist's response to the merchant
        """
        result = catalog_agent(message)
        return result.message

    @tool
    def handle_voice(message: str) -> str:
        """Route voice/audio message to the voice specialist for Hindi ASR processing.
        Use this when:
        - Merchant sends a voice recording or audio message
        - Message contains an S3 key reference to an audio file
        - Message mentions voice command or audio input
        - The API indicates this is a voice/audio message

        Args:
            message: The message containing audio S3 key or voice command info

        Returns:
            The voice specialist's response including transcript and action taken
        """
        result = voice_agent(message)
        return result.message

    @tool
    def handle_orders(message: str) -> str:
        """Route message to the order specialist for order management and savings.
        Use this when:
        - Merchant asks about orders, deliveries, or order status
        - Merchant wants to accept, reject, or track an order
        - Merchant asks about commission savings or earnings
        - Merchant asks for daily/weekly summary or "aaj ka hisaab"
        - Merchant wants to see a demo order or test order flow
        - Message mentions order, delivery, commission, savings, or "kitna kamaaya"

        Args:
            message: The merchant's message about orders or savings

        Returns:
            The order specialist's response to the merchant
        """
        result = order_agent(message)
        return result.message

    @tool
    def handle_intelligence(message: str) -> str:
        """Route message to the intelligence specialist for business insights.
        Use this when:
        - Merchant asks for morning brief or daily summary ("subah ka brief", "morning brief")
        - Merchant asks about stock levels or stock alerts ("stock kya hai", "kya khatam hone wala hai")
        - Merchant asks for price comparison with competitors ("price compare karo", "competitor price")
        - Merchant asks about demand forecast or festival predictions ("demand forecast", "festival prediction", "holi pe kya demand hogi")
        - Merchant asks general business intelligence questions ("aaj kitne order", "revenue kitna", "business kaise chal raha hai")

        Args:
            message: The merchant's message about business intelligence

        Returns:
            The intelligence specialist's response with insights and recommendations
        """
        result = intelligence_agent(message)
        return result.message

    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    agent = Agent(
        model=model,
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
        tools=[handle_onboarding, handle_catalog, handle_voice, handle_orders, handle_intelligence],
    )

    return agent
