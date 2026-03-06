"""Create IAM roles for Vyapari.ai — AgentCore, Lambda, Bedrock KB"""

import json
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "YOUR_ACCOUNT_ID")
iam = boto3.client("iam", region_name=REGION)


def create_role(role_name: str, trust_policy: dict, description: str) -> str:
    """Create IAM role, skip if exists. Returns role ARN."""
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
            MaxSessionDuration=3600,
        )
        arn = response["Role"]["Arn"]
        print(f"Created role: {role_name} ({arn})")
        return arn
    except iam.exceptions.EntityAlreadyExistsException:
        arn = f"arn:aws:iam::{ACCOUNT_ID}:role/{role_name}"
        print(f"Role already exists: {role_name} ({arn})")
        return arn


def attach_policy(role_name: str, policy_arn: str):
    """Attach managed policy to role."""
    try:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        print(f"  Attached: {policy_arn.split('/')[-1]} → {role_name}")
    except Exception as e:
        print(f"  Warning attaching policy: {e}")


def put_inline_policy(role_name: str, policy_name: str, policy_doc: dict):
    """Put inline policy on role."""
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_doc),
    )
    print(f"  Inline policy: {policy_name} → {role_name}")


def create_agentcore_role():
    """Role for Bedrock AgentCore Runtime to execute agents."""
    role_name = "vyapari-agentcore-role"
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                        "bedrock.amazonaws.com",
                        "bedrock-agentcore.amazonaws.com",
                    ]
                },
                "Action": "sts:AssumeRole",
            }
        ],
    }
    arn = create_role(role_name, trust, "Vyapari AgentCore execution role")

    # Bedrock full access (invoke models, KB)
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonBedrockFullAccess")

    # DynamoDB access for agent tools
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess")

    # S3 access for photos, voice, KB
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonS3FullAccess")

    # Transcribe for voice agent
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess")

    # Polly for voice responses
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonPollyFullAccess")

    # Translate for multilingual
    attach_policy(role_name, "arn:aws:iam::aws:policy/TranslateFullAccess")

    # CloudWatch for observability
    attach_policy(role_name, "arn:aws:iam::aws:policy/CloudWatchFullAccess")

    return arn


def create_lambda_role():
    """Role for Lambda functions (API handlers)."""
    role_name = "vyapari-lambda-role"
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    arn = create_role(role_name, trust, "Vyapari Lambda execution role")

    # Basic Lambda execution (CloudWatch logs)
    attach_policy(
        role_name,
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )

    # DynamoDB access
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess")

    # S3 access
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonS3FullAccess")

    # Bedrock invoke (to call AgentCore Runtime)
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonBedrockFullAccess")

    # SQS for async processing
    attach_policy(role_name, "arn:aws:iam::aws:policy/AmazonSQSFullAccess")

    return arn


def create_bedrock_kb_role():
    """Role for Bedrock Knowledge Base to access S3 data source."""
    role_name = "vyapari-bedrock-kb-role"
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": ACCOUNT_ID},
                },
            }
        ],
    }
    arn = create_role(role_name, trust, "Vyapari Bedrock KB role for S3 access")

    # S3 read access for KB data source
    kb_s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:ListBucket"],
                "Resource": [
                    f"arn:aws:s3:::vyapari-product-kb-{ACCOUNT_ID}",
                    f"arn:aws:s3:::vyapari-product-kb-{ACCOUNT_ID}/*",
                ],
            }
        ],
    }
    put_inline_policy(role_name, "vyapari-kb-s3-access", kb_s3_policy)

    # Bedrock model invocation for embeddings
    kb_bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["bedrock:InvokeModel"],
                "Resource": [
                    f"arn:aws:bedrock:{REGION}::foundation-model/amazon.nova-2-multimodal-embeddings-v1:0",
                ],
            }
        ],
    }
    put_inline_policy(role_name, "vyapari-kb-bedrock-access", kb_bedrock_policy)

    return arn


if __name__ == "__main__":
    print("Creating IAM roles for Vyapari.ai...\n")

    print("--- AgentCore Role ---")
    agentcore_arn = create_agentcore_role()

    print("\n--- Lambda Role ---")
    lambda_arn = create_lambda_role()

    print("\n--- Bedrock KB Role ---")
    kb_arn = create_bedrock_kb_role()

    print(f"\n=== Summary ===")
    print(f"AgentCore Role: {agentcore_arn}")
    print(f"Lambda Role:    {lambda_arn}")
    print(f"Bedrock KB Role: {kb_arn}")
    print("\nDone!")
