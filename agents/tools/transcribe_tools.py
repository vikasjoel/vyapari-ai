"""Transcribe tools — Hindi speech-to-text via Amazon Transcribe."""

import json
import time
import uuid
import os

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
VOICE_BUCKET = os.getenv("S3_VOICE_BUCKET", "vyapari-voice")
LANGUAGE = os.getenv("TRANSCRIBE_LANGUAGE", "hi-IN")

transcribe = boto3.client("transcribe", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


@tool
def transcribe_audio(s3_key: str, language_code: str = "hi-IN") -> str:
    """Transcribe an audio file stored in S3 using Amazon Transcribe.

    Args:
        s3_key: S3 object key for the audio file in the voice bucket
        language_code: Language code for transcription (default: hi-IN for Hindi)

    Returns:
        JSON with transcript text, confidence, and job details
    """
    job_name = f"vyapari-{uuid.uuid4().hex[:12]}"
    media_uri = f"s3://{VOICE_BUCKET}/{s3_key}"

    # Detect media format from extension
    ext = s3_key.rsplit(".", 1)[-1].lower() if "." in s3_key else "webm"
    format_map = {
        "webm": "webm",
        "ogg": "ogg",
        "wav": "wav",
        "mp3": "mp3",
        "mp4": "mp4",
        "flac": "flac",
    }
    media_format = format_map.get(ext, "webm")

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat=media_format,
            LanguageCode=language_code,
            Settings={
                "ShowSpeakerLabels": False,
                "ShowAlternatives": False,
            },
        )

        # Poll for completion (max 60 seconds)
        for _ in range(30):
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]

            if job_status == "COMPLETED":
                # Get transcript from result URI
                result_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                # Download and parse transcript
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(result_uri, context=ctx) as response:
                    transcript_data = json.loads(response.read().decode())

                transcript_text = transcript_data["results"]["transcripts"][0]["transcript"]

                # Cleanup job
                try:
                    transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                except Exception:
                    pass

                return json.dumps({
                    "status": "success",
                    "transcript": transcript_text,
                    "language": language_code,
                    "job_name": job_name,
                })

            elif job_status == "FAILED":
                reason = status["TranscriptionJob"].get("FailureReason", "Unknown")
                return json.dumps({
                    "status": "error",
                    "message": f"Transcription failed: {reason}",
                    "job_name": job_name,
                })

            time.sleep(2)

        return json.dumps({
            "status": "error",
            "message": "Transcription timed out after 60 seconds",
            "job_name": job_name,
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
        })


@tool
def upload_voice_to_s3(session_id: str, audio_base64: str, file_extension: str = "webm") -> str:
    """Upload a voice recording to S3 for transcription.

    Args:
        session_id: Chat session ID
        audio_base64: Base64-encoded audio data
        file_extension: Audio file extension (webm, ogg, wav, mp3)

    Returns:
        JSON with s3_key for the uploaded audio
    """
    import base64

    audio_id = uuid.uuid4().hex[:8]
    s3_key = f"recordings/{session_id}/{audio_id}.{file_extension}"

    audio_bytes = base64.b64decode(audio_base64)
    content_types = {
        "webm": "audio/webm",
        "ogg": "audio/ogg",
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
    }

    s3.put_object(
        Bucket=VOICE_BUCKET,
        Key=s3_key,
        Body=audio_bytes,
        ContentType=content_types.get(file_extension, "audio/webm"),
    )

    return json.dumps({
        "status": "uploaded",
        "s3_key": s3_key,
        "bucket": VOICE_BUCKET,
    })
