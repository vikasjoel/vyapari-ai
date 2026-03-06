"""Translate tools — multilingual translation via Amazon Translate."""

import json
import os

import boto3
from dotenv import load_dotenv
from strands import tool

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
translate = boto3.client("translate", region_name=REGION)


@tool
def translate_text(text: str, source_lang: str = "hi", target_lang: str = "en") -> str:
    """Translate text between languages using Amazon Translate.

    Args:
        text: The text to translate
        source_lang: Source language code (hi=Hindi, en=English, ta=Tamil, te=Telugu, bn=Bengali)
        target_lang: Target language code

    Returns:
        JSON with translated text
    """
    try:
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang,
        )

        return json.dumps({
            "status": "success",
            "translated_text": response["TranslatedText"],
            "source_lang": source_lang,
            "target_lang": target_lang,
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
        })
