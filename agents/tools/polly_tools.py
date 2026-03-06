"""Polly tools — Hindi text-to-speech via Amazon Polly."""

import json
import uuid
import os
import base64

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
VOICE_BUCKET = os.getenv("S3_VOICE_BUCKET", "vyapari-voice")
VOICE_ID = os.getenv("POLLY_VOICE_ID", "Aditi")
LANGUAGE = os.getenv("POLLY_LANGUAGE", "hi-IN")

polly = boto3.client("polly", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


@tool
def synthesize_speech(text: str, language_code: str = "hi-IN", voice_id: str = "Aditi") -> str:
    """Convert text to speech using Amazon Polly and store in S3.

    Args:
        text: The text to convert to speech (Hindi or English)
        language_code: Language code (hi-IN for Hindi, en-IN for Indian English)
        voice_id: Polly voice ID (Aditi for Hindi, Kajal for Indian English Neural)

    Returns:
        JSON with S3 key and presigned URL for the audio file
    """
    try:
        # Use standard engine for Aditi (neural not available for all voices)
        engine = "standard"
        if voice_id in ("Kajal",):
            engine = "neural"

        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            LanguageCode=language_code,
            Engine=engine,
        )

        audio_bytes = response["AudioStream"].read()

        # Upload to S3
        audio_id = uuid.uuid4().hex[:8]
        s3_key = f"responses/{audio_id}.mp3"

        s3.put_object(
            Bucket=VOICE_BUCKET,
            Key=s3_key,
            Body=audio_bytes,
            ContentType="audio/mpeg",
        )

        # Generate presigned URL
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": VOICE_BUCKET, "Key": s3_key},
            ExpiresIn=86400,
        )

        return json.dumps({
            "status": "success",
            "s3_key": s3_key,
            "audio_url": presigned_url,
            "audio_size_bytes": len(audio_bytes),
            "voice_id": voice_id,
            "language": language_code,
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
        })
