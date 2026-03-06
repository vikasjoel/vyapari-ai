"""Voice Agent — Hindi ASR/TTS, intent detection, and action routing."""

from strands import Agent
from strands.models.bedrock import BedrockModel
from agents.prompts.voice_prompt import VOICE_SYSTEM_PROMPT
from agents.tools.transcribe_tools import transcribe_audio, upload_voice_to_s3
from agents.tools.polly_tools import synthesize_speech
from agents.tools.translate_tools import translate_text
from agents.tools.ondc_tools import get_catalog, update_product

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


def create_voice_agent() -> Agent:
    """Create the voice agent with ASR, TTS, and catalog tools."""
    model = BedrockModel(
        model_id=MODEL_ID,
        region_name=REGION,
    )

    agent = Agent(
        model=model,
        system_prompt=VOICE_SYSTEM_PROMPT,
        tools=[
            transcribe_audio,
            upload_voice_to_s3,
            synthesize_speech,
            translate_text,
            get_catalog,
            update_product,
        ],
    )

    return agent
