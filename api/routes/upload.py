"""POST /api/upload — photo upload for catalog generation."""

import uuid
import os
import base64
from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from api.services.agent_service import invoke_agent

router = APIRouter()

import boto3
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
PHOTOS_BUCKET = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")
s3 = boto3.client("s3", region_name=REGION)


@router.post("/upload")
async def upload_photo(
    photo: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    language: Optional[str] = Form("hi"),
):
    session_id = session_id or str(uuid.uuid4())

    # Read and upload to S3
    contents = await photo.read()
    s3_key = f"uploads/{session_id}/{photo.filename}"
    s3.put_object(
        Bucket=PHOTOS_BUCKET,
        Key=s3_key,
        Body=contents,
        ContentType=photo.content_type or "image/jpeg",
    )

    # Send to agent with S3 reference
    agent_message = (
        f"Merchant uploaded a shelf photo. S3 key: {s3_key}. "
        f"Please analyze this photo and create a product catalog."
    )
    if message:
        agent_message = f"{message}. Photo S3 key: {s3_key}"

    result = invoke_agent(session_id, agent_message, language=language or "hi")

    return {
        "session_id": session_id,
        "response": result["response"],
        "agent_activity": result.get("agent_activity"),
    }
