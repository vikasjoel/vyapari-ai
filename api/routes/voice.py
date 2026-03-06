"""POST /api/voice — voice recording upload and processing."""

import uuid
import os
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from api.services.agent_service import invoke_agent

router = APIRouter()

import boto3
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
VOICE_BUCKET = os.getenv("S3_VOICE_BUCKET", "vyapari-voice")
s3 = boto3.client("s3", region_name=REGION)


@router.post("/voice")
async def process_voice(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    sample_command: Optional[str] = Form(None),
    language: Optional[str] = Form("hi"),
):
    session_id = session_id or str(uuid.uuid4())

    # Read and upload to S3
    contents = await audio.read()
    s3_key = f"recordings/{session_id}/{uuid.uuid4()}.webm"
    s3.put_object(
        Bucket=VOICE_BUCKET,
        Key=s3_key,
        Body=contents,
        ContentType="audio/webm",
    )

    # Transcribe audio first
    import json as json_mod
    from agents.tools import transcribe_tools

    try:
        # Call the underlying transcribe function (unwrapped)
        transcribe_result_json = transcribe_tools.transcribe_audio.__wrapped__(s3_key=s3_key, language_code="hi-IN")
        transcribe_result = json_mod.loads(transcribe_result_json)

        if transcribe_result.get("status") == "success":
            transcript = transcribe_result.get("transcript", "")
        else:
            transcript = "[Transcription failed]"
    except Exception as e:
        transcript = f"[Could not transcribe: {str(e)}]"

    # Send transcribed text to agent for routing
    agent_message = f"{transcript}"

    result = invoke_agent(session_id, agent_message, language=language or "hi")

    # Prepend transcript confirmation to response
    if result.get("response"):
        result["response"] = f"🎤 **मैंने सुना**: \"{transcript}\"\n\n{result['response']}"

    return {
        "session_id": session_id,
        "response": result["response"],
        "agent_activity": result.get("agent_activity"),
    }
