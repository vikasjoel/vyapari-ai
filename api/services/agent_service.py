"""Agent service — manages supervisor agent and sessions."""

import logging
import os
import re
import time
from typing import Optional

import boto3
from dotenv import load_dotenv

from agents.supervisor import create_supervisor_agent

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
MERCHANTS_TABLE = os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants")
dynamodb = boto3.resource("dynamodb", region_name=REGION)

log = logging.getLogger(__name__)

# Session-level agent instances — keyed by session_id
_agents: dict = {}

# Language context prefixes — prepended to messages so agents respond in correct language
LANGUAGE_PREFIXES = {
    "hi": "",  # Hindi is default — no prefix needed
    "en": "[RESPOND IN ENGLISH] ",
    "ta": "[RESPOND IN TAMIL (தமிழ்)] ",
    "te": "[RESPOND IN TELUGU (తెలుగు)] ",
    "bn": "[RESPOND IN BENGALI (বাংলা)] ",
}


def _clean_response(text: str) -> str:
    """Clean up agent response — remove meta-commentary, raw URLs, internal data."""
    if not isinstance(text, str):
        return str(text)

    # Remove raw S3 presigned URLs (contain AWSAccessKeyId, Signature, etc.)
    text = re.sub(
        r'https?://[^\s]*AWSAccessKeyId[^\s]*',
        '🔊 Voice response तैयार है',
        text,
    )
    # Remove any remaining raw S3 URLs with long query strings
    text = re.sub(
        r'https?://[^\s]*\.s3[^\s]*\?[^\s]{100,}',
        '🔊 Voice response तैयार है',
        text,
    )
    # Remove markdown-style links with S3 URLs
    text = re.sub(
        r'\[.*?\]\(https?://[^\)]*\.s3[^\)]*\)',
        '🔊 Voice response तैयार है',
        text,
    )

    return text.strip()


def get_or_create_agent(session_id: str):
    """Get existing agent for session or create new one."""
    if session_id not in _agents:
        _agents[session_id] = {
            "agent": create_supervisor_agent(),
            "merchant_id": None,
            "language": "hi",
            "created_at": time.time(),
        }
    return _agents[session_id]


def invoke_agent(session_id: str, message: str, language: str = "hi") -> dict:
    """Invoke the supervisor agent with a message."""
    session = get_or_create_agent(session_id)
    agent = session["agent"]
    session["language"] = language

    # Prepend language context if not Hindi
    prefix = LANGUAGE_PREFIXES.get(language, "")
    agent_message = f"{prefix}{message}" if prefix else message

    start = time.time()
    try:
        result = agent(agent_message)
        latency_ms = int((time.time() - start) * 1000)

        response_text = result.message
        # Handle dict responses
        if isinstance(response_text, dict):
            content = response_text.get("content", [])
            if isinstance(content, list) and content:
                response_text = content[0].get("text", str(content))
            else:
                response_text = str(response_text)

        # Clean up response text
        response_text = _clean_response(response_text)

        # Detect merchant_id — try multiple patterns
        if not get_merchant_id(session_id):
            # Pattern 1: raw JSON "merchant_id": "uuid"
            mid_match = re.search(r'"merchant_id"\s*:\s*"([0-9a-f-]{36})"', response_text)
            if mid_match:
                set_merchant_id(session_id, mid_match.group(1))
            else:
                # Pattern 2: ONDC seller ID in formatted text → look up in DynamoDB
                seller_match = re.search(r'ONDC-([A-F0-9]{8})', response_text)
                if seller_match:
                    seller_id = f"ONDC-{seller_match.group(1)}"
                    try:
                        table = dynamodb.Table(MERCHANTS_TABLE)
                        resp = table.scan(
                            FilterExpression="ondc_seller_id = :sid",
                            ExpressionAttributeValues={":sid": seller_id},
                            Limit=1,
                        )
                        items = resp.get("Items", [])
                        if items:
                            set_merchant_id(session_id, items[0]["merchant_id"])
                    except Exception:
                        log.debug("Could not look up merchant by seller ID %s", seller_id)

        return {
            "response": response_text,
            "merchant_id": get_merchant_id(session_id),
            "agent_activity": {
                "latencyMs": latency_ms,
                "language": language,
            },
        }
    except Exception as e:
        latency_ms = int((time.time() - start) * 1000)
        log.exception("Agent invocation failed for session %s", session_id)
        error_messages = {
            "hi": "माफ़ कीजिए, कुछ technical problem आ गई। कृपया दोबारा try करें। 🙏",
            "en": "Sorry, something went wrong. Please try again. 🙏",
            "ta": "மன்னிக்கவும், ஏதோ தொழில்நுட்ப சிக்கல் ஏற்பட்டது. மீண்டும் முயற்சிக்கவும். 🙏",
            "te": "క్షమించండి, ఏదో సమస్య వచ్చింది. దయచేసి మళ్ళీ ప్రయత్నించండి. 🙏",
        }
        return {
            "response": error_messages.get(language, error_messages["hi"]),
            "agent_activity": {
                "latencyMs": latency_ms,
                "language": language,
                "error": str(e),
            },
        }


def set_merchant_id(session_id: str, merchant_id: str):
    """Store merchant_id for a session."""
    if session_id in _agents:
        _agents[session_id]["merchant_id"] = merchant_id


def get_merchant_id(session_id: str) -> Optional[str]:
    """Get merchant_id for a session."""
    return _agents.get(session_id, {}).get("merchant_id")
