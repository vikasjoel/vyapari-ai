"""S3 tools — photo and voice file upload/download."""

import uuid
import os
import base64

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
PHOTOS_BUCKET = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")
VOICE_BUCKET = os.getenv("S3_VOICE_BUCKET", "vyapari-voice")

s3 = boto3.client("s3", region_name=REGION)


@tool
def upload_photo(session_id: str, photo_base64: str, file_extension: str = "jpg") -> str:
    """Upload a photo to S3 and return the S3 key.

    Args:
        session_id: Chat session ID for organizing uploads
        photo_base64: Base64-encoded image data
        file_extension: File extension (jpg, png, webp)

    Returns:
        JSON with s3_key and presigned URL
    """
    photo_id = str(uuid.uuid4())[:8]
    s3_key = f"uploads/{session_id}/{photo_id}.{file_extension}"

    image_bytes = base64.b64decode(photo_base64)
    content_types = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}

    s3.put_object(
        Bucket=PHOTOS_BUCKET,
        Key=s3_key,
        Body=image_bytes,
        ContentType=content_types.get(file_extension, "image/jpeg"),
    )

    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": PHOTOS_BUCKET, "Key": s3_key},
        ExpiresIn=86400,
    )

    return f'{{"status": "uploaded", "s3_key": "{s3_key}", "bucket": "{PHOTOS_BUCKET}", "url": "{presigned_url}"}}'


@tool
def get_photo_url(s3_key: str) -> str:
    """Get a presigned URL for a photo in S3.

    Args:
        s3_key: The S3 object key for the photo

    Returns:
        Presigned URL string valid for 24 hours
    """
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": PHOTOS_BUCKET, "Key": s3_key},
        ExpiresIn=86400,
    )
    return presigned_url
