# Vyapari.ai — System Architecture

## 1. Architecture Overview

Vyapari.ai is a **multi-agent AI system** deployed on Amazon Bedrock AgentCore that enables Indian merchants to operate on ONDC (Open Network for Digital Commerce) through Hindi voice commands and shelf photographs.

The system follows an **Agent Supervisor Pattern** where a central Supervisor Agent orchestrates 4 specialist agents, each with distinct capabilities and tools, running on AgentCore Runtime with persistent memory, secure tool access via Gateway, and full observability.

```
                    ┌─────────────────────────────────────────┐
                    │           CLIENT INTERFACES              │
                    │                                          │
                    │  ┌─────────────┐   ┌──────────────────┐ │
                    │  │  React Web  │   │  WhatsApp (via   │ │
                    │  │  App (Live  │   │  Twilio sandbox  │ │
                    │  │  URL for    │   │  — video demo    │ │
                    │  │  judges)    │   │  only)           │ │
                    │  └──────┬──────┘   └────────┬─────────┘ │
                    └─────────┼──────────────────┼────────────┘
                              │                  │
                              ▼                  ▼
                    ┌─────────────────────────────────────────┐
                    │          API LAYER (FastAPI)              │
                    │                                          │
                    │  POST /api/chat      Text messages       │
                    │  POST /api/upload    Photo uploads        │
                    │  POST /api/voice     Voice recordings     │
                    │  GET  /api/catalog   Buyer catalog view   │
                    │                                          │
                    │  Hosted on: Lambda + API Gateway          │
                    │  OR ECS Fargate (if latency matters)     │
                    └────────────────┬────────────────────────┘
                                     │
                                     │ boto3 InvokeAgentRuntime
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                 AMAZON BEDROCK AGENTCORE RUNTIME                          │
│                 (Serverless, Session-Isolated MicroVMs)                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │                    🎯 SUPERVISOR AGENT                             │  │
│  │                    (Strands Agents + Claude Sonnet 4)              │  │
│  │                                                                    │  │
│  │  Responsibilities:                                                 │  │
│  │  • Analyze incoming message (text/photo/voice)                    │  │
│  │  • Route to appropriate specialist agent                          │  │
│  │  • Manage smooth handoffs between agents                          │  │
│  │  • Maintain coherent merchant experience                          │  │
│  │  • Return agent_activity metadata for observability               │  │
│  │                                                                    │  │
│  │  Routing Logic:                                                    │  │
│  │  new_user/no_profile → Onboarding Agent                          │  │
│  │  photo_uploaded      → Catalog Agent                              │  │
│  │  voice_note          → Voice Agent (→ may re-route)               │  │
│  │  text_about_orders   → Order Agent                                │  │
│  │  text_about_products → Catalog Agent                              │  │
│  │  returning_user      → Check Memory, resume where left off        │  │
│  │                                                                    │  │
│  └────┬──────────────┬──────────────┬──────────────┬─────────────────┘  │
│       │              │              │              │                     │
│       ▼              ▼              ▼              ▼                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────────┐           │
│  │ 📋      │   │ 📸      │   │ 📦      │   │ 🎤          │           │
│  │ONBOARD- │   │CATALOG  │   │ORDER    │   │VOICE        │           │
│  │ING      │   │AGENT    │   │AGENT    │   │AGENT        │           │
│  │AGENT    │   │         │   │         │   │             │           │
│  │         │   │         │   │         │   │             │           │
│  │Tools:   │   │Tools:   │   │Tools:   │   │Tools:       │           │
│  │•save_   │   │•analyze_│   │•get_    │   │•transcribe_ │           │
│  │ merchant│   │ photo   │   │ orders  │   │ audio       │           │
│  │•check_  │   │•search_ │   │•accept_ │   │•synthesize_ │           │
│  │ dup     │   │ kb      │   │ order   │   │ speech      │           │
│  │•start_  │   │•save_   │   │•calc_   │   │•translate_  │           │
│  │ ondc_reg│   │ catalog │   │ savings │   │ text        │           │
│  │         │   │•gen_    │   │•gen_    │   │•route_to_   │           │
│  │         │   │ beckn   │   │ summary │   │ agent       │           │
│  └─────────┘   └─────────┘   └─────────┘   └─────────────┘           │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  AGENTCORE MEMORY                                                  │  │
│  │                                                                    │  │
│  │  Short-Term Memory (STM):                                         │  │
│  │  • Current conversation history                                    │  │
│  │  • Collected onboarding slots                                      │  │
│  │  • Active agent context                                            │  │
│  │  • Photo processing state                                          │  │
│  │                                                                    │  │
│  │  Long-Term Memory (LTM):                                          │  │
│  │  • Merchant profile (name, shop, location, type)                  │  │
│  │  • Catalog summary (product count, categories)                    │  │
│  │  • Order history summary                                          │  │
│  │  • Language preference                                             │  │
│  │  • Last interaction timestamp                                      │  │
│  │                                                                    │  │
│  │  Episodic Memory:                                                  │  │
│  │  • Patterns from past merchants (product distributions by region) │  │
│  │  • Common corrections (pricing patterns)                          │  │
│  │  • Catalog accuracy improvements over time                        │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  AGENTCORE GATEWAY (MCP Server)                                    │  │
│  │                                                                    │  │
│  │  Exposes these tools securely to all agents:                       │  │
│  │                                                                    │  │
│  │  DynamoDB Tools:                                                   │  │
│  │  • save_merchant(data) → vyapari-merchants table                  │  │
│  │  • get_merchant(merchant_id) → merchant profile                   │  │
│  │  • save_catalog(merchant_id, products) → vyapari-products table   │  │
│  │  • update_product(product_id, updates) → update single product    │  │
│  │  • get_catalog(merchant_id) → full product list                   │  │
│  │  • save_order(order_data) → vyapari-orders table                  │  │
│  │  • get_orders(merchant_id, status) → filtered orders              │  │
│  │                                                                    │  │
│  │  Bedrock Tools:                                                    │  │
│  │  • analyze_photo(image_bytes) → Claude multimodal → products JSON │  │
│  │  • search_product_kb(image_bytes) → KB visual similarity → match  │  │
│  │                                                                    │  │
│  │  Voice Tools:                                                      │  │
│  │  • transcribe_audio(audio, lang) → Amazon Transcribe → text       │  │
│  │  • synthesize_speech(text, lang) → Amazon Polly → audio bytes     │  │
│  │  • translate_text(text, src, tgt) → Amazon Translate → text       │  │
│  │                                                                    │  │
│  │  Commerce Tools:                                                   │  │
│  │  • generate_beckn_schema(products) → ONDC Beckn catalog format    │  │
│  │  • simulate_order(merchant_id) → mock ONDC order                  │  │
│  │  • calculate_savings(total, category) → commission comparison     │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  AGENTCORE OBSERVABILITY                                           │  │
│  │                                                                    │  │
│  │  Metrics (via CloudWatch):                                         │  │
│  │  • Token usage per agent per session                               │  │
│  │  • Latency per agent action                                        │  │
│  │  • Session duration                                                │  │
│  │  • Error rates per agent                                           │  │
│  │  • Tool invocation counts                                          │  │
│  │                                                                    │  │
│  │  Traces (OpenTelemetry):                                           │  │
│  │  • End-to-end request trace across agent handoffs                 │  │
│  │  • Per-span detail: Supervisor → Agent → Tool → Response          │  │
│  │  • Memory read/write events                                        │  │
│  │  • KB search latency and match quality                            │  │
│  │                                                                    │  │
│  │  Dashboards:                                                       │  │
│  │  • Agent performance overview                                      │  │
│  │  • Quality metrics (fed to frontend Agent Activity Panel)         │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
         │                              │                    │
         ▼                              ▼                    ▼
┌──────────────────┐  ┌──────────────────────────┐  ┌────────────────────┐
│  BEDROCK          │  │  DATA LAYER               │  │  AI SERVICES       │
│  KNOWLEDGE BASE   │  │                           │  │                    │
│                   │  │  DynamoDB Tables:          │  │  Transcribe:       │
│  Nova Multimodal  │  │  • vyapari-merchants      │  │  Hindi ASR         │
│  Embeddings V1    │  │  • vyapari-products       │  │  Custom vocab      │
│                   │  │  • vyapari-orders          │  │                    │
│  5000+ Indian     │  │  • vyapari-sessions        │  │  Polly:            │
│  FMCG product     │  │                           │  │  Hindi Neural TTS  │
│  images           │  │  S3 Buckets:              │  │  Voice: Aditi      │
│                   │  │  • vyapari-photos          │  │                    │
│  Visual search:   │  │  • vyapari-product-kb      │  │  Translate:        │
│  image query →    │  │  • vyapari-voice           │  │  hi ↔ ta,te,bn,en │
│  top-3 matches    │  │  • vyapari-web             │  │                    │
│  with confidence  │  │                           │  │  Bedrock Claude:   │
│                   │  │  CloudFront:              │  │  Sonnet 4          │
│                   │  │  • Web app CDN             │  │  Multimodal        │
└──────────────────┘  └──────────────────────────┘  └────────────────────┘
```

---

## 2. Data Flow Diagrams

### 2.1 Merchant Onboarding Flow

```
Merchant                    API          Supervisor      Onboarding       DynamoDB
   │                        │               │             Agent              │
   │ "Main Ramesh hoon,     │               │               │               │
   │  Delhi mein store hai" │               │               │               │
   │───────────────────────►│               │               │               │
   │                        │  invoke       │               │               │
   │                        │──────────────►│               │               │
   │                        │               │  new_user     │               │
   │                        │               │──────────────►│               │
   │                        │               │               │ extract:      │
   │                        │               │               │ name=Ramesh   │
   │                        │               │               │ loc=Delhi     │
   │                        │               │               │ type=kirana   │
   │                        │               │               │               │
   │                        │               │               │ check_dup()   │
   │                        │               │               │──────────────►│
   │                        │               │               │◄──────────────│
   │                        │               │               │ no duplicate  │
   │                        │               │               │               │
   │                        │               │               │ Memory: store │
   │                        │               │               │ partial profile│
   │                        │               │               │               │
   │ "Aapki dukaan ka      │               │◄──────────────│               │
   │  naam kya hai?"       │◄──────────────│               │               │
   │◄──────────────────────│               │               │               │
   │                        │               │               │               │
   │ "Ramesh General Store" │               │               │               │
   │───────────────────────►│──────────────►│──────────────►│               │
   │                        │               │               │ 4/5 slots     │
   │                        │               │               │ ask phone     │
   │◄──────────────────────│◄──────────────│◄──────────────│               │
   │                        │               │               │               │
   │ "9876543210"           │               │               │               │
   │───────────────────────►│──────────────►│──────────────►│               │
   │                        │               │               │ ALL 5 slots!  │
   │                        │               │               │ save_merchant │
   │                        │               │               │──────────────►│
   │                        │               │               │◄──────────────│
   │                        │               │               │ saved ✅      │
   │                        │               │               │               │
   │ "Registered! Ab        │               │  handoff to   │               │
   │  photos bhejiye"      │◄──────────────│  catalog_agent │               │
   │◄──────────────────────│               │               │               │
```

### 2.2 Photo-to-Catalog Flow (with Knowledge Base)

```
Merchant          API          Supervisor    Catalog Agent   Bedrock     Knowledge    DynamoDB
   │               │               │               │        Claude         Base          │
   │ 📷 photo     │               │               │          │             │             │
   │──────────────►│               │               │          │             │             │
   │               │ S3 upload     │               │          │             │             │
   │               │───────►S3     │               │          │             │             │
   │               │               │               │          │             │             │
   │               │ invoke        │               │          │             │             │
   │               │──────────────►│               │          │             │             │
   │               │               │ photo →       │          │             │             │
   │               │               │──────────────►│          │             │             │
   │               │               │               │          │             │             │
   │               │               │               │ analyze_ │             │             │
   │               │               │               │ photo()  │             │             │
   │               │               │               │─────────►│             │             │
   │               │               │               │          │ multimodal  │             │
   │               │               │               │          │ analysis    │             │
   │               │               │               │◄─────────│             │             │
   │               │               │               │ 23 products            │             │
   │               │               │               │ 4 uncertain            │             │
   │               │               │               │ (confidence < 0.8)     │             │
   │               │               │               │          │             │             │
   │               │               │               │ For each uncertain:    │             │
   │               │               │               │ search_  │             │             │
   │               │               │               │ kb()     │             │             │
   │               │               │               │──────────────────────►│             │
   │               │               │               │          │  visual     │             │
   │               │               │               │          │  similarity │             │
   │               │               │               │          │  search     │             │
   │               │               │               │◄──────────────────────│             │
   │               │               │               │ 4 KB matches          │             │
   │               │               │               │ (Haldiram 95%,        │             │
   │               │               │               │  MDH 91%, etc.)       │             │
   │               │               │               │          │             │             │
   │               │               │               │ Merge:                │             │
   │               │               │               │ 19 vision + 4 KB     │             │
   │               │               │               │ = 23 total products   │             │
   │               │               │               │          │             │             │
   │               │               │               │ save_catalog()        │             │
   │               │               │               │─────────────────────────────────────►│
   │               │               │               │◄─────────────────────────────────────│
   │               │               │               │          │             │             │
   │ "23 products  │               │◄──────────────│          │             │             │
   │  found! ✅"   │◄──────────────│               │          │             │             │
   │ + product     │               │               │          │             │             │
   │   cards       │               │               │          │             │             │
   │◄──────────────│               │               │          │             │             │
```

### 2.3 Voice Command Flow

```
Merchant      API       Supervisor   Voice Agent   Transcribe   Bedrock    Catalog    Polly
   │           │             │            │             │         Claude     Agent       │
   │ 🎤 voice │             │            │             │           │          │         │
   │ "Amul ka │             │            │             │           │          │         │
   │  rate 32 │             │            │             │           │          │         │
   │  karo"   │             │            │             │           │          │         │
   │──────────►│             │            │             │           │          │         │
   │           │ S3 upload   │            │             │           │          │         │
   │           │────►S3      │            │             │           │          │         │
   │           │ invoke      │            │             │           │          │         │
   │           │────────────►│            │             │           │          │         │
   │           │             │ voice →    │             │           │          │         │
   │           │             │───────────►│             │           │          │         │
   │           │             │            │ transcribe  │           │          │         │
   │           │             │            │ _audio()    │           │          │         │
   │           │             │            │────────────►│           │          │         │
   │           │             │            │◄────────────│           │          │         │
   │           │             │            │ "Amul ka rate           │          │         │
   │           │             │            │  32 karo"               │          │         │
   │           │             │            │             │           │          │         │
   │           │             │            │ detect intent           │          │         │
   │           │             │            │────────────────────────►│          │         │
   │           │             │            │◄────────────────────────│          │         │
   │           │             │            │ intent: UPDATE_PRICE    │          │         │
   │           │             │            │ product: Amul Gold Milk │          │         │
   │           │             │            │ new_price: 32           │          │         │
   │           │             │            │             │           │          │         │
   │           │             │            │ route to Catalog Agent  │          │         │
   │           │             │            │────────────────────────────────────►│         │
   │           │             │            │             │           │          │ update  │
   │           │             │            │             │           │          │ DynamoDB│
   │           │             │            │◄────────────────────────────────────│         │
   │           │             │            │ "Updated ✅"│           │          │         │
   │           │             │            │             │           │          │         │
   │           │             │            │ synthesize_ │           │          │         │
   │           │             │            │ speech()    │           │          │         │
   │           │             │            │──────────────────────────────────────────────►│
   │           │             │            │◄──────────────────────────────────────────────│
   │           │             │            │ Hindi audio response    │          │         │
   │           │             │◄───────────│             │           │          │         │
   │           │◄────────────│ text + audio             │          │         │
   │◄──────────│             │             │            │           │          │         │
   │ "Amul Gold│             │             │            │           │          │         │
   │  ka rate  │             │             │            │           │          │         │
   │  ₹32 ✅"  │             │             │            │           │          │         │
   │ + 🔊 audio│             │             │            │           │          │         │
```

---

## 3. Agent Design Specifications

### 3.1 Supervisor Agent

**Model:** Claude Sonnet 4 via Bedrock (`us.anthropic.claude-sonnet-4-20250514`)
**Framework:** Strands Agents
**Deployment:** AgentCore Runtime

**Tools (sub-agents):**
- `onboarding_agent` — registered as callable tool
- `catalog_agent` — registered as callable tool
- `order_agent` — registered as callable tool
- `voice_agent` — registered as callable tool

**Routing Decision Tree:**
```
incoming_message
├── contains photo/image?
│   └── YES → catalog_agent
├── contains audio/voice?
│   └── YES → voice_agent
├── is new user (no merchant_id in memory)?
│   └── YES → onboarding_agent
├── text mentions: order, delivery, commission, savings, paisa?
│   └── YES → order_agent
├── text mentions: product, price, rate, stock, catalog, photo, khatam?
│   └── YES → catalog_agent
├── text is greeting (namaste, hello, hi)?
│   ├── returning user (merchant_id in memory)?
│   │   └── YES → check last state, resume
│   └── NO → onboarding_agent
└── UNCLEAR → ask clarifying question
```

**Handoff Protocol:**
When one agent completes its task, it returns a `handoff_suggestion`:
```json
{
  "response": "Registration complete!",
  "handoff_suggestion": {
    "next_agent": "catalog_agent",
    "context": "Merchant registered, ready for catalog creation",
    "message_to_merchant": "Ab aapki dukaan ki photos bhejiye!"
  }
}
```
Supervisor picks up the handoff and routes next message to suggested agent.

### 3.2 Onboarding Agent

**Required Slots:**
```python
SLOTS = {
    "merchant_name": {"type": str, "required": True, "hindi": "naam"},
    "shop_name": {"type": str, "required": True, "hindi": "dukaan ka naam"},
    "shop_type": {"type": str, "required": True, "hindi": "dukaan ka type",
                  "valid": ["kirana", "restaurant", "pharmacy", "repair", "textile", "other"]},
    "location": {"type": str, "required": True, "hindi": "jagah/sheher"},
    "phone": {"type": str, "required": True, "hindi": "phone number",
              "validation": r"^[6-9]\d{9}$"}  # Indian mobile number
}
```

**Dynamic Slot Extraction Behavior:**
The agent MUST extract ALL recognizable information from EVERY merchant message, not ask one question at a time. Example:

Input: "Haan bhai, main Ramesh hoon, Lajpat Nagar mein kirana chalata hoon"
Expected extraction: name=Ramesh, location=Lajpat Nagar, type=kirana (3 of 5 slots)
Next question: only ask for shop_name and phone

This is the key behavioral innovation — conversational, not form-like.

### 3.3 Catalog Agent

**Input Processing:**
1. Receive image bytes (from S3 or direct upload)
2. Send to Bedrock Claude Sonnet 4 with multimodal prompt
3. Parse JSON response (product list)
4. For each product with confidence < 0.8:
   - Crop product region from original image (if possible) OR use full image
   - Send to Bedrock Knowledge Base for visual similarity search
   - If KB returns match with score > 0.85, use KB data to fill/correct product info
   - Mark product `source: "knowledge_base"`
5. Store all products in DynamoDB
6. Generate ONDC Beckn schema
7. Return product cards + summary to merchant

**Bedrock Claude Multimodal Call:**
```python
import boto3
import json
import base64

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def analyze_photo(image_bytes: bytes) -> list[dict]:
    response = bedrock.invoke_model(
        modelId='us.anthropic.claude-sonnet-4-20250514',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64.b64encode(image_bytes).decode()
                        }
                    },
                    {
                        "type": "text",
                        "text": CATALOG_VISION_PROMPT  # Detailed prompt from prompts/catalog_prompt.py
                    }
                ]
            }]
        })
    )
    result = json.loads(response['body'].read())
    products_json = result['content'][0]['text']
    return json.loads(products_json)['products']
```

**Knowledge Base Query:**
```python
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def search_product_kb(image_bytes: bytes, kb_id: str) -> list[dict]:
    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={
            'multimodalInputList': [{
                'content': {
                    'byteContent': base64.b64encode(image_bytes).decode()
                },
                'modality': 'IMAGE'
            }]
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 3
            }
        }
    )
    matches = []
    for result in response.get('retrievalResults', []):
        matches.append({
            'score': result.get('score', 0),
            'source_uri': result.get('location', {}).get('s3Location', {}).get('uri', ''),
            'metadata': result.get('metadata', {})
        })
    return matches
```

### 3.4 Voice Agent

**Voice Pipeline:**
```
Audio bytes → S3 upload → Transcribe (hi-IN) → transcript
    → Claude intent detection → {intent, params, confidence}
        → if CATALOG action → route to Catalog Agent
        → if ORDER action → route to Order Agent  
        → if SIMPLE query → handle directly
    → Generate confirmation text
    → Polly (hi-IN, Neural, Aditi) → audio response bytes
    → Return text + audio to frontend
```

**Custom Vocabulary (Transcribe):**
```json
{
  "Phrases": [
    {"Phrase": "Amul", "SoundsLike": ["amul", "aamul"]},
    {"Phrase": "Aashirvaad", "SoundsLike": ["aashirvaad", "ashirwad"]},
    {"Phrase": "Haldiram", "SoundsLike": ["haldiram", "haldiraam"]},
    {"Phrase": "Maggi", "SoundsLike": ["maggi", "maagi"]},
    {"Phrase": "Parle", "SoundsLike": ["parle", "parale"]},
    {"Phrase": "Britannia", "SoundsLike": ["britannia", "britania"]},
    {"Phrase": "Patanjali", "SoundsLike": ["patanjali", "patanjli"]},
    {"Phrase": "Dabur", "SoundsLike": ["dabur", "dabar"]},
    {"Phrase": "Surf Excel", "SoundsLike": ["surf excel", "sarf eksel"]},
    {"Phrase": "khatam", "SoundsLike": ["khatam", "katam"]},
    {"Phrase": "udhaar", "SoundsLike": ["udhaar", "udhar"]},
    {"Phrase": "ONDC", "SoundsLike": ["ondc", "o n d c"]}
  ]
}
```

### 3.5 Order Agent

**Commission Rates (hardcoded for demo):**
```python
COMMISSION_RATES = {
    "swiggy": {"food": 0.35, "grocery": 0.18},
    "zomato": {"food": 0.28, "grocery": 0.15},
    "blinkit": {"grocery": 0.18},
    "ondc": {"food": 0.09, "grocery": 0.08, "default": 0.10}
}
```

**Order Simulation:**
Generates realistic orders by pulling random products from the merchant's actual DynamoDB catalog, with realistic quantities and customer names.

---

## 4. Knowledge Base Design

### Purpose
Pre-indexed reference database of 2,000-5,000 common Indian FMCG product images. Enables visual similarity search to identify products that Claude's multimodal analysis isn't confident about.

### S3 Structure
```
s3://vyapari-product-kb/
├── dairy/
│   ├── amul-gold-milk-500ml.jpg
│   ├── amul-taaza-milk-500ml.jpg
│   ├── mother-dairy-toned-500ml.jpg
│   ├── amul-butter-100g.jpg
│   └── ...
├── staples/
│   ├── aashirvaad-atta-5kg.jpg
│   ├── fortune-sunflower-oil-1l.jpg
│   ├── tata-salt-1kg.jpg
│   └── ...
├── snacks/
│   ├── lays-classic-52g.jpg
│   ├── haldiram-bhujia-200g.jpg
│   ├── parle-g-biscuit-100g.jpg
│   └── ...
├── beverages/
├── personal_care/
├── household/
├── spices/
└── metadata/
    └── products.json     # Product name, brand, MRP, category, HSN per image
```

### Metadata Format (products.json)
```json
[
  {
    "image_key": "dairy/amul-gold-milk-500ml.jpg",
    "name_en": "Amul Gold Full Cream Milk 500ml",
    "name_hi": "अमूल गोल्ड फुल क्रीम दूध 500ml",
    "brand": "Amul",
    "mrp": 32,
    "category": "Dairy",
    "subcategory": "Milk",
    "hsn_code": "0401",
    "ondc_category": "Grocery>Dairy>Milk"
  }
]
```

### KB Configuration
```python
# Embedding model: Amazon Nova Multimodal Embeddings V1
# Dimensions: 1024 (balance of accuracy and cost)
# Vector store: S3 Vectors (managed by Bedrock)
# Parsing: Native multimodal (no BDA needed — images only)
```

---

## 5. Frontend Architecture

### Component Tree
```
App
├── DemoGuide (overlay — first-time visitors)
├── ChatInterface (main view)
│   ├── Header (logo, language toggle, reset button)
│   ├── MessageList
│   │   ├── ChatBubble (bot messages)
│   │   ├── ChatBubble (user messages)
│   │   ├── ProductCard (inline product display)
│   │   ├── OrderCard (inline order notification)
│   │   └── ProgressIndicator (loading states)
│   ├── AgentActivityPanel (collapsible)
│   │   ├── ActiveAgentBadge
│   │   ├── ToolCallTrace
│   │   └── MetricsDisplay (latency, tokens)
│   └── InputBar
│       ├── PhotoUpload (+ sample photos)
│       ├── VoiceRecorder (+ pre-recorded commands)
│       └── TextInput
└── BuyerCatalogView (separate route: /catalog/:id)
    ├── ShopHeader
    ├── CategoryTabs
    └── ProductGrid
```

### State Management
No external library. React useState for:
```typescript
interface ChatState {
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  merchantId: string | null;
  catalogReady: boolean;
  agentActivity: AgentActivity[];
  language: 'hi' | 'ta' | 'te' | 'en';
}
```

### API Communication
```typescript
// services/api.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function sendMessage(sessionId: string | null, message: string, language: string) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, language })
  });
  return response.json();
}

export async function uploadPhoto(sessionId: string, file: File) {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('photo', file);
  const response = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
  return response.json();
}

export async function sendVoice(sessionId: string, audioBlob: Blob, sampleCommand?: string) {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('audio', audioBlob, 'recording.webm');
  if (sampleCommand) formData.append('sample_command', sampleCommand);
  const response = await fetch(`${API_BASE}/voice`, { method: 'POST', body: formData });
  return response.json();
}

export async function getCatalog(merchantId: string) {
  const response = await fetch(`${API_BASE}/catalog/${merchantId}`);
  return response.json();
}
```

---

## 6. ONDC Beckn Schema (Reference)

Products generated by the Catalog Agent are stored in DynamoDB in our internal format AND can be exported as ONDC Beckn-compliant JSON:

```json
{
  "context": {
    "domain": "ONDC:RET10",
    "action": "on_search",
    "country": "IND",
    "city": "std:011",
    "bap_id": "buyer-app.com",
    "bpp_id": "vyapari.ai",
    "transaction_id": "txn-uuid",
    "timestamp": "2026-03-01T10:00:00.000Z"
  },
  "message": {
    "catalog": {
      "bpp/providers": [{
        "id": "merchant-uuid",
        "descriptor": {
          "name": "Ramesh Ki Dukaan",
          "short_desc": "Kirana store in Lajpat Nagar",
          "images": [{"url": "https://s3.../shop.jpg"}]
        },
        "locations": [{
          "id": "loc-1",
          "gps": "28.5695,77.2370",
          "address": {"city": "New Delhi", "area_code": "110024"}
        }],
        "items": [
          {
            "id": "prod-uuid-001",
            "descriptor": {
              "name": "Amul Gold Full Cream Milk 500ml",
              "short_desc": "अमूल गोल्ड फुल क्रीम दूध",
              "images": [{"url": "https://s3.../product.jpg"}]
            },
            "price": {"currency": "INR", "value": "32", "maximum_value": "35"},
            "category_id": "Grocery",
            "quantity": {"available": {"count": "100"}, "maximum": {"count": "100"}},
            "tags": [
              {"code": "origin", "list": [{"code": "country", "value": "IND"}]},
              {"code": "veg_nonveg", "list": [{"code": "veg", "value": "yes"}]}
            ]
          }
        ]
      }]
    }
  }
}
```

This schema is generated by `agents/tools/ondc_tools.py → generate_beckn_schema()`.

---

## 7. Deployment Architecture

### Production (Hackathon)
```
                    Internet
                       │
                       ▼
               CloudFront CDN
               (vyapari-web S3)
                       │
                       ▼
              API Gateway (REST)
                       │
                       ▼
            Lambda / ECS Fargate
            (FastAPI application)
                       │
                       ▼
          AgentCore Runtime (us-east-1)
          ├── Supervisor Agent
          ├── Onboarding Agent (via tool)
          ├── Catalog Agent (via tool)
          ├── Order Agent (via tool)
          └── Voice Agent (via tool)
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     DynamoDB     S3 Buckets    Bedrock KB
     (ap-south-1   (us-east-1)  (us-east-1)
      or us-east-1)
```

### Key Deployment Decision: Region
- AgentCore Runtime: deploy in `us-east-1` or `us-west-2` (verified GA)
- DynamoDB/S3: ideally `ap-south-1` (Mumbai) for data residency story, but can be same region as AgentCore for simplicity in hackathon
- In submission/blog: note "Production deployment targets ap-south-1 for data residency compliance"

### AgentCore Deployment Commands
```bash
# Install toolkit
pip install bedrock-agentcore-starter-toolkit

# Create agent project
agentcore create

# Configure (pick Strands Agents, Claude Sonnet 4, enable Memory)
agentcore configure -e agents/supervisor.py

# Deploy
agentcore launch

# Check status
agentcore status

# Invoke (test)
python scripts/test_agents.py
```

---

## 8. Security Considerations (Hackathon Scope)

- **No auth** on web app (hackathon demo — judges need frictionless access)
- **IAM roles** for all AWS service access (never hardcode credentials)
- **CORS** configured on API Gateway to allow CloudFront origin only
- **S3** buckets not publicly accessible (use presigned URLs for media)
- **Rate limiting** on API Gateway (prevent abuse during evaluation period)
- **Cost guardrails**: DynamoDB on-demand pricing, Bedrock usage alerts in CloudWatch
- **Session isolation**: AgentCore Runtime provides MicroVM isolation per session

---

## 9. Monitoring & Alerting

### CloudWatch Alarms (set up for evaluation period)
- Bedrock throttling errors > 0 → alarm
- API Gateway 5xx errors > 5 in 5 minutes → alarm
- DynamoDB consumed capacity > 80% → alarm
- Lambda errors > 0 → alarm

### AgentCore Observability Metrics to Track
- Average agent response latency (target: < 5s for text, < 15s for photo analysis)
- Token consumption per session (budget: ~20K tokens per full merchant journey)
- Agent handoff success rate (target: 100% for demo flows)
- KB search hit rate (target: > 80% for common products)
