"""Test the voice agent — Polly TTS, Transcribe ASR, and full pipeline."""

import sys
import json
sys.path.insert(0, ".")

import boto3
import os
from dotenv import load_dotenv
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
VOICE_BUCKET = os.getenv("S3_VOICE_BUCKET", "vyapari-voice")


def test_polly_tts():
    """Test Hindi text-to-speech."""
    print("=== Test 1: Polly TTS (Hindi) ===\n")

    from agents.tools.polly_tools import synthesize_speech

    result = synthesize_speech(
        text="नमस्ते! आपका ऑर्डर तैयार है। कुल रकम 245 रुपये है।",
        language_code="hi-IN",
        voice_id="Aditi",
    )
    data = json.loads(result)

    if data.get("status") == "success":
        print(f"✅ TTS Success: {data['audio_size_bytes']} bytes")
        print(f"   Voice: {data['voice_id']}, Language: {data['language']}")
        print(f"   S3 Key: {data['s3_key']}")
        print(f"   URL: {data['audio_url'][:80]}...")
    else:
        print(f"❌ Error: {data}")


def test_transcribe_roundtrip():
    """Test: generate speech with Polly, then transcribe it back with Transcribe."""
    print("\n=== Test 2: Polly → S3 → Transcribe Roundtrip ===\n")

    from agents.tools.polly_tools import synthesize_speech
    from agents.tools.transcribe_tools import transcribe_audio

    # Step 1: Generate Hindi speech
    test_text = "अमूल का रेट बत्तीस रुपये कर दो"
    print(f"Original text: {test_text}")

    polly = boto3.client("polly", region_name=REGION)
    response = polly.synthesize_speech(
        Text=test_text,
        OutputFormat="mp3",
        VoiceId="Aditi",
        LanguageCode="hi-IN",
        Engine="standard",
    )
    audio_bytes = response["AudioStream"].read()
    print(f"Generated audio: {len(audio_bytes)} bytes")

    # Step 2: Upload to S3 (in voice bucket)
    s3 = boto3.client("s3", region_name=REGION)
    s3_key = "test/roundtrip_test.mp3"
    s3.put_object(Bucket=VOICE_BUCKET, Key=s3_key, Body=audio_bytes, ContentType="audio/mpeg")
    print(f"Uploaded to s3://{VOICE_BUCKET}/{s3_key}")

    # Step 3: Transcribe
    print("Transcribing (this may take 10-30 seconds)...")
    result = transcribe_audio(s3_key=s3_key, language_code="hi-IN")
    data = json.loads(result)

    if data.get("status") == "success":
        print(f"✅ Transcript: \"{data['transcript']}\"")
        print(f"   (Original: \"{test_text}\")")
    else:
        print(f"❌ Error: {data}")

    # Cleanup
    s3.delete_object(Bucket=VOICE_BUCKET, Key=s3_key)
    print("Cleaned up test audio")


def test_voice_agent_with_text():
    """Test voice agent with a simulated text transcript (skip ASR for speed)."""
    print("\n=== Test 3: Voice Agent Intent Detection ===\n")

    from agents.voice_agent import create_voice_agent

    agent = create_voice_agent()

    # Simulate: merchant sent voice, we already have transcript
    print("Simulating voice command: 'Amul ka rate 35 karo'")
    result = agent(
        "A merchant sent a voice command. The transcript is: 'Amul ka rate 35 karo'. "
        "Detect the intent and respond. Also generate a voice response using synthesize_speech."
    )
    print(f"\nAgent response:\n{result.message}\n")


if __name__ == "__main__":
    test_polly_tts()
    test_transcribe_roundtrip()
    test_voice_agent_with_text()
    print("\n=== All Voice Tests Complete ===")
