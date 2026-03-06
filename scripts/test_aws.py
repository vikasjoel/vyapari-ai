"""Quick smoke test of all AWS services needed for Vyapari.ai"""

import json
import boto3
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")


def test_dynamodb():
    """Test DynamoDB put/get on merchants table."""
    print("=== DynamoDB ===")
    ddb = boto3.resource("dynamodb", region_name=REGION)
    table = ddb.Table(os.getenv("DYNAMODB_MERCHANTS_TABLE", "vyapari-merchants"))

    test_id = f"test-{uuid.uuid4().hex[:8]}"
    table.put_item(Item={"merchant_id": test_id, "name": "Test Merchant", "phone": "+919999999999"})
    resp = table.get_item(Key={"merchant_id": test_id})
    item = resp.get("Item", {})
    assert item["name"] == "Test Merchant", f"Expected 'Test Merchant', got {item.get('name')}"
    table.delete_item(Key={"merchant_id": test_id})
    print(f"  PUT/GET/DELETE: OK (test_id={test_id})")


def test_s3():
    """Test S3 upload/download on photos bucket."""
    print("=== S3 ===")
    s3 = boto3.client("s3", region_name=REGION)
    bucket = os.getenv("S3_PHOTOS_BUCKET", "vyapari-photos")

    test_key = "test/hello.txt"
    s3.put_object(Bucket=bucket, Key=test_key, Body=b"namaste")
    resp = s3.get_object(Bucket=bucket, Key=test_key)
    body = resp["Body"].read().decode()
    assert body == "namaste", f"Expected 'namaste', got '{body}'"
    s3.delete_object(Bucket=bucket, Key=test_key)
    print(f"  PUT/GET/DELETE: OK (bucket={bucket})")


def test_bedrock():
    """Test Bedrock Claude Sonnet 4 invocation."""
    print("=== Bedrock (Claude Sonnet 4) ===")
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)
    model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514")

    resp = bedrock.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "Say 'Namaste' in Hindi script. One word only."}],
        }),
    )
    result = json.loads(resp["body"].read())
    text = result["content"][0]["text"]
    print(f"  Invoke: OK → {text.strip()}")


def test_transcribe():
    """Test Transcribe API access."""
    print("=== Transcribe ===")
    transcribe = boto3.client("transcribe", region_name=REGION)
    jobs = transcribe.list_transcription_jobs(MaxResults=1)
    print(f"  ListJobs: OK (count={len(jobs.get('TranscriptionJobSummaries', []))})")


def test_polly():
    """Test Polly Hindi TTS."""
    print("=== Polly ===")
    polly = boto3.client("polly", region_name=REGION)
    resp = polly.synthesize_speech(
        Text="नमस्ते",
        OutputFormat="mp3",
        VoiceId="Aditi",
        LanguageCode="hi-IN",
    )
    audio_bytes = resp["AudioStream"].read()
    print(f"  SynthesizeSpeech: OK ({len(audio_bytes)} bytes)")


def test_translate():
    """Test Translate Hindi→English."""
    print("=== Translate ===")
    translate = boto3.client("translate", region_name=REGION)
    resp = translate.translate_text(
        Text="नमस्ते, मैं रमेश हूँ",
        SourceLanguageCode="hi",
        TargetLanguageCode="en",
    )
    print(f"  Translate: OK → {resp['TranslatedText']}")


if __name__ == "__main__":
    print("Testing AWS services for Vyapari.ai...\n")
    tests = [test_dynamodb, test_s3, test_bedrock, test_transcribe, test_polly, test_translate]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1
        print()

    print(f"Results: {passed} passed, {failed} failed out of {len(tests)}")
