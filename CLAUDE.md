# Project: Vyapari.ai

> AI Commerce Copilot for Bharat — Multi-agent system on Amazon Bedrock AgentCore that onboards India's merchants onto ONDC through Hindi voice commands and shelf photos.

**Status:** New — Hackathon MVP Build
**Type:** Full Stack (Python Backend + React Frontend + AWS Agentic AI)
**Primary Language:** Python 3.10+ (backend/agents), TypeScript (frontend)
**Hackathon:** AWS AI for Bharat 2026 — Professional Track
**Deadline:** ~19 days to working MVP + video + blog

---

## Overview

Vyapari.ai is an AI-powered commerce copilot that serves as the intelligence layer between Indian merchants and ONDC (Open Network for Digital Commerce). It uses a multi-agent architecture on Amazon Bedrock AgentCore where 4 specialist AI agents — coordinated by a supervisor — autonomously handle merchant onboarding, product catalog creation from photos, order management, and Hindi voice interactions.

**Who it's for:** India's 63 million MSMEs — kirana store owners, restaurant operators, pharmacists — who can't navigate English seller dashboards but can send WhatsApp voice notes and photos.

**Key Innovation:** Not a chatbot calling an API. A team of agents deployed on AgentCore Runtime with persistent memory (STM + LTM + Episodic), a multimodal product Knowledge Base (Nova Embeddings), and real-time observability — all through a conversational Hindi interface.

**Success Criteria:**
1. Judge opens live URL → interacts with AI agents in Hindi → sees catalog generated from photos → sees order with commission savings
2. 3-minute video shows the full merchant journey on WhatsApp
3. GitHub passes code review
4. Blog on AWS Builder Center explains the AgentCore architecture

---

## Architecture

See `ARCHITECTURE.md` for full system design. Summary:

### System Components

```
Merchant (Web/WhatsApp) → API Gateway → Supervisor Agent (AgentCore Runtime)
                                            ├── Onboarding Agent (registration, slot-filling)
                                            ├── Catalog Agent (photos → ONDC catalog + KB search)
                                            ├── Order Agent (orders, savings, fulfillment)
                                            └── Voice Agent (Transcribe → intent → route → Polly)
                                                    │
                                        ┌───────────┼───────────┐
                                        ▼           ▼           ▼
                                   AgentCore    AgentCore    AgentCore
                                   Memory       Gateway      Observability
                                        │           │           │
                                        ▼           ▼           ▼
                              DynamoDB/S3    Tools(Bedrock,   CloudWatch
                                             Transcribe,     Dashboards
                                             Polly,KB,ONDC)
```

### Key Architecture Decisions

- **Why AgentCore Runtime (not Lambda + Bedrock direct):** Multi-agent orchestration with session isolation, persistent memory, built-in observability. Shows production-grade thinking. AWS's flagship 2026 product.
- **Why Strands Agents framework:** Python-native, minimal boilerplate, first-class AgentCore integration. `agentcore create` bootstraps deployment in minutes.
- **Why Bedrock Claude Sonnet 4 (not Nova):** Best multimodal performance for messy shelf photos. Best Hindi understanding. Best structured JSON output for catalog generation.
- **Why Multimodal Knowledge Base with Nova Embeddings:** Visual similarity search fills gaps when Claude can't fully identify a product. Turns "best effort" into "production-grade accurate."
- **Why DynamoDB (not RDS):** Single-digit ms reads for real-time catalog and order state. Serverless. Scales to zero. Natural key-value fit.
- **Why React frontend (not just WhatsApp):** Judges need a live URL to test (Step 3 of evaluation). WhatsApp API approval takes weeks. Web app with WhatsApp styling gives judges interactive access while video shows real WhatsApp flow.

---

## Tech Stack

### Backend (Agents + API)
- Python 3.10+ (AgentCore requirement)
- Strands Agents SDK (`strands-agents`)
- Bedrock AgentCore SDK (`bedrock-agentcore`)
- Bedrock AgentCore Starter Toolkit (`bedrock-agentcore-starter-toolkit`)
- boto3 (AWS SDK for DynamoDB, S3, Transcribe, Polly, Translate, Bedrock KB)
- FastAPI (API layer for web frontend)
- uvicorn (ASGI server)
- Pydantic v2 (request/response validation)

### Frontend (Web App for Judges)
- React 18 with TypeScript
- Vite for bundling
- TailwindCSS for styling
- No state management library needed (React useState/useReducer sufficient for chat)

### AI/ML Services
- Amazon Bedrock — Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-20250514`)
- Amazon Bedrock Knowledge Base — Nova Multimodal Embeddings V1 (`amazon.nova-embed-multimodal-v1:0`)
- Amazon Transcribe — Hindi ASR with custom vocabulary
- Amazon Polly — Hindi Neural TTS
- Amazon Translate — Hindi ↔ Tamil/Telugu/Bengali/English

### Infrastructure
- Amazon Bedrock AgentCore Runtime — host multi-agent system
- Amazon Bedrock AgentCore Memory — STM + LTM + Episodic
- Amazon Bedrock AgentCore Gateway — MCP server for tools
- Amazon Bedrock AgentCore Observability — CloudWatch traces
- Amazon DynamoDB — merchants, products, orders, sessions tables
- Amazon S3 — photos, voice recordings, product KB images, web app
- Amazon CloudFront — web app CDN
- Amazon API Gateway — REST API for web frontend
- AWS Lambda — API handlers, tool implementations
- Amazon SQS — async photo/voice processing
- Amazon CloudWatch — monitoring, agent dashboards

### Dev Tools
- uv (Python package manager — recommended by AgentCore docs)
- Docker (optional — only for local AgentCore testing)
- AWS CLI v2
- Git

---

## Project Structure

```
vyapari-ai/
├── CLAUDE.md                           # This file — project instructions
├── ARCHITECTURE.md                     # Detailed architecture document
├── README.md                           # GitHub README for judges
├── pyproject.toml                      # Python project config (uv)
├── requirements.txt                    # Python dependencies
│
├── agents/                             # AgentCore agent definitions
│   ├── __init__.py
│   ├── supervisor.py                   # Supervisor agent — routes to specialists
│   ├── onboarding_agent.py             # Merchant registration + slot filling
│   ├── catalog_agent.py                # Photo → ONDC catalog + KB search
│   ├── order_agent.py                  # Order management + savings calculator
│   ├── voice_agent.py                  # Hindi ASR/TTS + intent routing
│   ├── prompts/                        # System prompts for each agent
│   │   ├── supervisor_prompt.py
│   │   ├── onboarding_prompt.py
│   │   ├── catalog_prompt.py
│   │   ├── order_prompt.py
│   │   └── voice_prompt.py
│   └── tools/                          # Agent tools (registered via Gateway)
│       ├── __init__.py
│       ├── dynamodb_tools.py           # save_merchant, save_catalog, get_orders...
│       ├── s3_tools.py                 # upload_photo, get_photo...
│       ├── bedrock_tools.py            # analyze_photo (multimodal), search_kb...
│       ├── transcribe_tools.py         # transcribe_audio (Hindi ASR)
│       ├── polly_tools.py              # synthesize_speech (Hindi TTS)
│       ├── translate_tools.py          # translate_text (Hindi↔Tamil/Telugu)
│       └── ondc_tools.py              # generate_beckn_schema, simulate_order...
│
├── api/                                # FastAPI backend for web frontend
│   ├── __init__.py
│   ├── main.py                         # FastAPI app entry point
│   ├── routes/
│   │   ├── chat.py                     # POST /api/chat — text message to agent
│   │   ├── upload.py                   # POST /api/upload — photo upload
│   │   ├── voice.py                    # POST /api/voice — voice recording
│   │   ├── catalog.py                  # GET /api/catalog/{merchant_id} — buyer view
│   │   └── health.py                   # GET /api/health
│   ├── schemas/                        # Pydantic models
│   │   ├── chat.py                     # ChatRequest, ChatResponse
│   │   ├── merchant.py                 # MerchantProfile, OnboardingState
│   │   ├── product.py                  # Product, ONDCCatalogEntry
│   │   └── order.py                    # Order, CommissionSavings
│   ├── services/
│   │   ├── agent_service.py            # Invoke AgentCore Runtime
│   │   ├── media_service.py            # Handle photo/voice uploads to S3
│   │   └── session_service.py          # Manage chat sessions
│   └── config.py                       # Environment config, AWS settings
│
├── frontend/                           # React web app for judges
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── App.tsx                     # Main app with router
│       ├── main.tsx                    # Entry point
│       ├── components/
│       │   ├── ChatInterface.tsx       # WhatsApp-style chat UI
│       │   ├── ChatBubble.tsx          # Message bubble (bot/user)
│       │   ├── PhotoUpload.tsx         # Photo upload + sample photos
│       │   ├── VoiceRecorder.tsx       # Browser mic recording
│       │   ├── ProductCard.tsx         # Product display in chat
│       │   ├── OrderCard.tsx           # Order notification in chat
│       │   ├── AgentActivityPanel.tsx  # Real-time agent trace display
│       │   ├── BuyerCatalogView.tsx    # "Ramesh Ki Dukaan" buyer page
│       │   ├── LanguageToggle.tsx      # Hindi/Tamil/Telugu/English
│       │   └── DemoGuide.tsx           # First-time overlay for judges
│       ├── services/
│       │   ├── api.ts                  # HTTP client for backend
│       │   └── audioUtils.ts           # MediaRecorder helpers
│       ├── types/
│       │   └── index.ts               # TypeScript types
│       └── assets/
│           ├── sample-photos/          # Pre-loaded kirana shelf photos for judges
│           │   ├── snacks-shelf.jpg
│           │   ├── dairy-shelf.jpg
│           │   └── grocery-shelf.jpg
│           └── sample-voice/           # Pre-recorded Hindi voice commands
│               ├── price-update.webm
│               ├── out-of-stock.webm
│               ├── add-product.webm
│               └── catalog-query.webm
│
├── knowledge_base/                     # Product Intelligence KB
│   ├── setup_kb.py                     # Script to create Bedrock KB
│   ├── upload_products.py              # Upload product images to S3
│   ├── product_metadata/               # Product info JSON files
│   │   ├── dairy.json
│   │   ├── staples.json
│   │   ├── snacks.json
│   │   ├── beverages.json
│   │   ├── personal_care.json
│   │   └── household.json
│   └── images/                         # Product reference images (or S3 URIs)
│       └── README.md                   # Instructions to source images
│
├── infrastructure/                     # AWS infrastructure setup
│   ├── setup_aws.sh                    # Master setup script
│   ├── dynamodb_tables.py              # Create DynamoDB tables
│   ├── s3_buckets.sh                   # Create S3 buckets
│   ├── iam_roles.py                    # IAM roles for AgentCore, Lambda
│   ├── api_gateway.yaml                # API Gateway OpenAPI spec
│   ├── cloudformation/                 # Optional — IaC templates
│   │   └── template.yaml
│   └── .env.example                    # Environment variables template
│
├── scripts/                            # Helper scripts
│   ├── seed_demo_data.py               # Pre-populate DynamoDB with demo merchant
│   ├── simulate_orders.py              # Generate mock ONDC orders
│   ├── test_agents.py                  # Quick test of each agent
│   ├── deploy_agents.sh                # Deploy agents to AgentCore Runtime
│   └── deploy_frontend.sh             # Build + deploy React to S3/CloudFront
│
├── tests/
│   ├── test_onboarding_agent.py
│   ├── test_catalog_agent.py
│   ├── test_voice_agent.py
│   ├── test_order_agent.py
│   ├── test_supervisor.py
│   ├── test_api_endpoints.py
│   └── fixtures/
│       ├── sample_shelf_photos/        # Test images
│       ├── sample_voice_commands/      # Test audio files
│       └── expected_catalogs/          # Expected output JSON
│
└── docs/
    ├── product-spec.md                 # Full product specification
    ├── merchant-scenarios.md           # 10 merchant analyses
    ├── competitive-analysis.md         # vs Blinkit/JioMart/Swiggy
    ├── video-script.md                 # 3-minute video script
    └── blog-draft.md                   # AWS Builder Center blog
```

---

## Data Models

### DynamoDB Table: `vyapari-merchants`

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| merchant_id | String (UUID) | PK | Unique merchant identifier |
| phone | String | GSI-PK | Phone number (WhatsApp) |
| name | String | — | Merchant's full name |
| shop_name | String | — | Business name |
| shop_type | String | — | kirana, restaurant, pharmacy, repair, textile, other |
| location | Map | — | `{city, area, state, pincode, lat, lng}` |
| ondc_seller_id | String | — | ONDC registration ID |
| onboarding_status | String | — | registered, catalog_pending, live, suspended |
| languages | List[String] | — | `["hi", "en"]` |
| created_at | String (ISO) | — | Registration timestamp |
| updated_at | String (ISO) | — | Last update timestamp |

### DynamoDB Table: `vyapari-products`

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| product_id | String (UUID) | PK | Unique product identifier |
| merchant_id | String | GSI-PK | Owner merchant |
| name_en | String | — | English product name |
| name_hi | String | — | Hindi product name (Devanagari) |
| brand | String | — | Brand name |
| variant | String | — | Size/weight/flavor |
| price | Number | — | Price in INR |
| category | String | GSI-SK | ONDC category |
| subcategory | String | — | ONDC subcategory |
| description_hi | String | — | Hindi description |
| description_en | String | — | English description |
| image_url | String | — | S3 URL of product image |
| available | Boolean | — | In stock or not |
| is_loose_item | Boolean | — | Sold by weight without packaging |
| ondc_item_id | String | — | ONDC Beckn item ID |
| confidence | Number | — | AI identification confidence (0-1) |
| source | String | — | vision, knowledge_base, merchant_correction, voice |
| created_at | String (ISO) | — | Creation timestamp |
| updated_at | String (ISO) | — | Last update |

### DynamoDB Table: `vyapari-orders`

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| order_id | String (UUID) | PK | Unique order identifier |
| merchant_id | String | GSI-PK | Merchant receiving order |
| source | String | — | ondc, swiggy, zomato, direct |
| buyer_app | String | — | Paytm, Magicpin, Ola, etc. |
| customer_name | String | — | Buyer name |
| items | List[Map] | — | `[{product_id, name, qty, price}]` |
| total | Number | — | Order total in INR |
| commission_ondc | Number | — | ONDC commission amount |
| commission_swiggy | Number | — | Equivalent Swiggy commission |
| savings | Number | — | `commission_swiggy - commission_ondc` |
| status | String | — | new, accepted, preparing, ready, delivered, cancelled |
| created_at | String (ISO) | — | Order timestamp |

### DynamoDB Table: `vyapari-sessions`

| Attribute | Type | Key | Description |
|-----------|------|-----|-------------|
| session_id | String (UUID) | PK | Chat session ID |
| merchant_id | String | GSI-PK | Associated merchant (if registered) |
| active_agent | String | — | Current specialist agent handling session |
| onboarding_state | Map | — | `{slots_collected: {}, slots_missing: []}` |
| message_count | Number | — | Messages in this session |
| created_at | String (ISO) | — | Session start |
| last_active | String (ISO) | — | Last message timestamp |

---

## API Contracts

### Base URL
- Local dev: `http://localhost:8000/api`
- Production: `https://{cloudfront-url}/api`

### Authentication
No auth for hackathon MVP. Sessions identified by `session_id` (UUID generated on first message).

### Endpoints

#### POST /api/chat
Send a text message to the agent system.
```json
// Request
{
  "session_id": "uuid-string",      // null for new session
  "message": "Main Ramesh hoon, Lajpat Nagar mein kirana store hai",
  "language": "hi"                   // hi, en, ta, te
}

// Response
{
  "session_id": "uuid-string",
  "responses": [
    {
      "type": "text",
      "content": "Namaste Ramesh ji! Aapki dukaan ka naam kya hai?",
      "agent": "onboarding_agent"
    }
  ],
  "agent_activity": {
    "supervisor_routed_to": "onboarding_agent",
    "slots_extracted": {"name": "Ramesh", "location": "Lajpat Nagar", "type": "kirana"},
    "slots_missing": ["shop_name", "phone"],
    "memory_events": ["stored_merchant_profile"],
    "latency_ms": 2340,
    "tokens_used": 856
  }
}
```

#### POST /api/upload
Upload shelf photo for catalog generation.
```json
// Request (multipart/form-data)
{
  "session_id": "uuid-string",
  "photo": <binary file>,
  "message": "optional text with the photo"
}

// Response (streamed — products appear one by one)
{
  "session_id": "uuid-string",
  "responses": [
    {"type": "text", "content": "📸 Photo mil gayi! Analyzing...", "agent": "catalog_agent"},
    {"type": "progress", "content": "🔍 12 products identified so far..."},
    {"type": "product_card", "content": {
      "name_hi": "अमूल गोल्ड दूध 500ml", "name_en": "Amul Gold Milk 500ml",
      "price": 32, "category": "Dairy", "confidence": 0.95, "source": "vision"
    }},
    {"type": "product_card", "content": {
      "name_hi": "हल्दीराम आलू भुजिया 200g", "name_en": "Haldiram Aloo Bhujia 200g",
      "price": 45, "category": "Snacks", "confidence": 0.92, "source": "knowledge_base"
    }},
    {"type": "text", "content": "✅ 23 products found! ONDC pe publish karein?"}
  ],
  "agent_activity": {
    "supervisor_routed_to": "catalog_agent",
    "products_found": 23,
    "kb_matches": 4,
    "vision_only": 19,
    "latency_ms": 15200,
    "tokens_used": 12500
  }
}
```

#### POST /api/voice
Upload voice recording for processing.
```json
// Request (multipart/form-data)
{
  "session_id": "uuid-string",
  "audio": <binary file (webm/ogg/wav)>,
  "sample_command": "price-update"    // optional — for pre-recorded demo commands
}

// Response
{
  "session_id": "uuid-string",
  "transcript": "Amul ka rate 32 karo",
  "responses": [
    {"type": "text", "content": "🎤 Suna: \"Amul ka rate 32 karo\""},
    {"type": "text", "content": "✅ Amul Gold Milk ka rate ₹32 ho gaya!", "agent": "catalog_agent"},
    {"type": "audio_url", "content": "https://s3.../response_audio.mp3"}
  ],
  "agent_activity": {
    "voice_agent_action": "transcribe → detect_intent → route_to_catalog_agent",
    "intent": "UPDATE_PRICE",
    "params": {"product": "Amul Gold Milk", "new_price": 32},
    "transcribe_latency_ms": 1200,
    "total_latency_ms": 3400
  }
}
```

#### GET /api/catalog/{merchant_id}
Buyer-side catalog view.
```json
// Response
{
  "merchant": {
    "shop_name": "Ramesh Ki Dukaan",
    "location": "Lajpat Nagar, Delhi",
    "type": "kirana",
    "product_count": 47
  },
  "products": [
    {
      "product_id": "uuid",
      "name_hi": "अमूल गोल्ड दूध 500ml",
      "name_en": "Amul Gold Milk 500ml",
      "price": 32,
      "category": "Dairy",
      "image_url": "https://s3.../product.jpg",
      "available": true
    }
  ],
  "categories": ["Dairy", "Staples", "Snacks", "Beverages", "Personal Care"],
  "ondc_compliant": true
}
```

#### GET /api/health
```json
{"status": "ok", "agents": "running", "region": "us-east-1"}
```

---

## Implementation Phases

### Phase 1: AWS Foundation (Day 1)
- [ ] Create AWS account or use existing. Enable Bedrock model access in us-east-1:
  - Claude Sonnet 4 (`us.anthropic.claude-sonnet-4-20250514`)
  - Nova Multimodal Embeddings V1 (`amazon.nova-embed-multimodal-v1:0`)
- [ ] Install AgentCore starter toolkit: `pip install bedrock-agentcore-starter-toolkit`
- [ ] Install Strands Agents: `pip install strands-agents`
- [ ] Install `bedrock-agentcore` Python SDK
- [ ] Create DynamoDB tables: `vyapari-merchants`, `vyapari-products`, `vyapari-orders`, `vyapari-sessions`
- [ ] Create S3 buckets: `vyapari-photos`, `vyapari-product-kb`, `vyapari-voice`, `vyapari-web`
- [ ] Create IAM roles: AgentCore execution role, Lambda role, Bedrock KB role
- [ ] Test basic boto3 calls: Bedrock invoke, DynamoDB put/get, S3 upload
- [ ] Set up `.env` with all AWS config (region, bucket names, table names, model IDs)

**Checkpoint:** All AWS services accessible, tables/buckets created, basic SDK calls working.

### Phase 2: First Agent on AgentCore (Day 2)
- [ ] Create simple supervisor agent using Strands:
  ```python
  from strands import Agent
  from bedrock_agentcore.runtime import BedrockAgentCoreApp
  agent = Agent(model="us.anthropic.claude-sonnet-4-20250514")
  app = BedrockAgentCoreApp()
  @app.entrypoint
  def invoke(payload):
      result = agent(payload.get("prompt", "Namaste!"))
      return {"response": result.message}
  ```
- [ ] Deploy to AgentCore Runtime: `agentcore create` → `agentcore configure` → `agentcore launch`
- [ ] Verify invocation via boto3 `InvokeAgentRuntime`
- [ ] Configure AgentCore Memory (STM + LTM): `agentcore configure` with memory enabled
- [ ] Test memory persistence: send message, get response, send follow-up — agent should remember context
- [ ] Note the Agent ARN — needed for all subsequent invocations

**Checkpoint:** Agent deployed on AgentCore Runtime, invocable via SDK, memory working.

### Phase 3: Onboarding Agent (Day 3)
- [ ] Write `agents/prompts/onboarding_prompt.py` — full system prompt with dynamic slot-filling behavior
- [ ] Write `agents/tools/dynamodb_tools.py`:
  - `save_merchant(merchant_data)` → DynamoDB put_item
  - `check_duplicate(phone)` → DynamoDB query
  - `update_merchant(merchant_id, updates)` → DynamoDB update_item
- [ ] Write `agents/onboarding_agent.py` — Strands Agent with tools
- [ ] Register Onboarding Agent as a tool of Supervisor agent
- [ ] Test dynamic slot extraction:
  - Input: "Main Ramesh hoon, Delhi mein kirana store hai"
  - Expected: extracts name, location, type. Asks only for shop_name and phone.
- [ ] Test: "Mera naam Priya hai" → only name extracted, asks for remaining 4
- [ ] Test: full 5 messages → merchant registered in DynamoDB
- [ ] Test memory: close session, reopen → agent remembers merchant

**Checkpoint:** Onboarding Agent registers merchants through natural Hindi conversation with dynamic slot filling.

### Phase 4: Catalog Agent — Core (Day 4-5)
- [ ] Write `agents/prompts/catalog_prompt.py` — multimodal catalog generation prompt
- [ ] Write `agents/tools/bedrock_tools.py`:
  - `analyze_photo(image_bytes)` → Bedrock Claude Sonnet 4 multimodal invocation → JSON product list
  - CRITICAL: The prompt must ask Claude to return a JSON array of products with: name_en, name_hi, brand, variant, price, category, description_hi, is_loose_item, confidence
- [ ] Write `agents/tools/s3_tools.py`:
  - `upload_photo(session_id, photo_bytes)` → S3 put_object → return URL
  - `get_photo(s3_key)` → S3 get_object → return bytes
- [ ] Write `agents/tools/ondc_tools.py`:
  - `generate_beckn_schema(products)` → Transform product list to ONDC Beckn catalog format
- [ ] Write `agents/catalog_agent.py` — Agent with photo analysis + DynamoDB catalog storage
- [ ] Test with 5 different kirana shelf photos (source from Google Images or take real ones)
- [ ] Tune the multimodal prompt for accuracy — iterate until product names and prices are reasonable
- [ ] Test multi-photo: send 3 photos → agent combines results → total product count
- [ ] Test ONDC schema output: verify generated schema matches Beckn protocol format

**Checkpoint:** Send shelf photos → get accurate product catalog in Hindi + English with ONDC-compliant schema.

### Phase 5: Catalog Agent — Knowledge Base Enhancement (Day 5-6)
- [ ] Source 2,000-3,000 Indian product images. Organize by category in S3:
  - Top FMCG: Amul, HUL (Surf Excel, Vim, Dove), ITC (Aashirvaad, Sunfeast, Bingo), Dabur, Patanjali, Parle, Britannia, Haldiram, MDH, Everest, Fortune, Tata (Salt, Tea)
  - Include different package sizes/variants
  - Add metadata JSON with product_name, brand, MRP, category, HSN code
- [ ] Run `knowledge_base/setup_kb.py`:
  - Create Bedrock Knowledge Base with Nova Multimodal Embeddings V1
  - Configure S3 data source pointing to product images bucket
  - Sync and verify index status
- [ ] Write `agents/tools/bedrock_tools.py` → `search_product_kb(image_bytes)`:
  - Use `bedrock-agent-runtime` Retrieve API with image query
  - Return top 3 matches with confidence scores
- [ ] Integrate KB search into Catalog Agent:
  - When Claude multimodal confidence < 0.8 for a product, trigger KB visual search
  - Use KB result to fill in product details (name, brand, price)
  - Mark product `source: "knowledge_base"` in catalog
- [ ] Test with partially visible products — verify KB fills gaps
- [ ] Test with unusual/regional products — verify graceful fallback

**Checkpoint:** Catalog Agent uses both Claude vision + KB visual search. Uncertain products get KB-enhanced identification.

### Phase 6: Voice Agent (Day 7-8)
- [ ] Write `agents/tools/transcribe_tools.py`:
  - `transcribe_audio(audio_bytes, language="hi-IN")` → Amazon Transcribe StartTranscriptionJob or streaming
  - Create custom vocabulary: common Indian brand names, Hindi commerce terms
  - Return transcript text
- [ ] Write `agents/tools/polly_tools.py`:
  - `synthesize_speech(text, language="hi-IN", voice_id="Aditi")` → Amazon Polly SynthesizeSpeech
  - Return audio bytes (MP3)
  - Use Neural engine for natural voice
- [ ] Write `agents/prompts/voice_prompt.py` — intent detection from Hindi transcript
- [ ] Write `agents/voice_agent.py`:
  - Receive audio → Transcribe → intent detection → route to specialist OR execute directly
  - Generate voice response via Polly
  - Support intents: UPDATE_PRICE, MARK_OUT_OF_STOCK, ADD_PRODUCT, CATALOG_QUERY, SHARE_LINK
- [ ] Register as Supervisor tool. Test integration:
  - Voice note "Amul ka rate 32 karo" → Voice Agent → Catalog Agent → DynamoDB update → Polly confirmation
  - Voice note "Atta khatam ho gaya" → Voice Agent → Catalog Agent → mark out of stock
  - Voice note "Kitne products hain?" → Voice Agent → handles directly → responds with count
- [ ] Test Hindi-English code-switching: "Maggi ka price update karo, 14 rupees"
- [ ] Create custom vocabulary JSON with 50+ Indian brand names for Transcribe accuracy

**Checkpoint:** Hindi voice commands → transcribed → understood → executed → voice response in Hindi.

### Phase 7: Order Agent (Day 9)
- [ ] Write `agents/prompts/order_prompt.py` — order management in Hindi
- [ ] Write `scripts/simulate_orders.py` — generate realistic mock ONDC orders:
  - Random products from merchant's catalog
  - Random buyer names and buyer apps (Paytm, Magicpin, Ola)
  - Realistic quantities and totals
- [ ] Write `agents/order_agent.py`:
  - Format order notification in Hindi
  - Accept/reject handling
  - Commission calculator: compare ONDC (8-10%) vs Swiggy (25-35%) vs Zomato (22-30%)
  - Daily summary generator: total orders, revenue, total savings
- [ ] Write `agents/tools/ondc_tools.py` → `simulate_order(merchant_id)`:
  - Pull random products from merchant's DynamoDB catalog
  - Generate order with realistic details
  - Store in vyapari-orders table
- [ ] Test: trigger simulated order → notification in chat → accept → savings displayed

**Checkpoint:** Orders arrive, merchant accepts, commission savings calculated and displayed in Hindi.

### Phase 8: Supervisor Integration + Agent Handoffs (Day 10)
- [ ] Finalize `agents/supervisor.py`:
  - Route text → appropriate agent based on content analysis
  - Route photo → Catalog Agent
  - Route voice → Voice Agent
  - Handle handoffs: Onboarding complete → "Now send photos" → Catalog Agent
  - Handle handoffs: Catalog complete → auto-trigger Order Agent for first simulated order
- [ ] Test full journey end-to-end:
  1. New message "Namaste" → Supervisor → Onboarding Agent
  2. Complete registration → "Ab photos bhejiye"
  3. Upload photos → Supervisor → Catalog Agent → catalog generated
  4. Voice command → Supervisor → Voice Agent → Catalog Agent → price updated
  5. Order arrives → Supervisor → Order Agent → notification → accept → savings
- [ ] Verify AgentCore Memory across the full journey:
  - STM: conversation context maintained through agent handoffs
  - LTM: merchant profile persists across sessions
- [ ] Test agent activity data: verify each agent logs its actions for the Activity Panel
- [ ] Stress test: run journey 5x. Fix any inconsistencies.

**Checkpoint:** Full merchant journey works end-to-end across all 4 agents with smooth handoffs.

### Phase 9: Web App Frontend (Day 11-12)
- [ ] Initialize React project: `npm create vite@latest frontend -- --template react-ts`
- [ ] Install TailwindCSS, configure
- [ ] Build `ChatInterface.tsx`:
  - WhatsApp-green styling (#075e54 header, #ece5dd background, #dcf8c6 user bubbles, white bot bubbles)
  - Message list with auto-scroll
  - Text input with send button
  - Photo upload button (triggers file picker)
  - Voice record button (browser MediaRecorder API)
  - Language toggle: [Hindi] [Tamil] [English]
  - Reset button for judges
- [ ] Build `ChatBubble.tsx` — renders text, product cards, order cards, audio player
- [ ] Build `ProductCard.tsx` — displays product from catalog (name_hi, price, category, confidence badge)
- [ ] Build `OrderCard.tsx` — displays order notification with accept/reject buttons + savings
- [ ] Build `PhotoUpload.tsx`:
  - File upload for custom photos
  - 3 sample photo thumbnails: "🏪 Snacks Shelf", "🏪 Dairy Shelf", "🏪 Grocery Shelf"
  - Click sample → auto-sends to backend
- [ ] Build `VoiceRecorder.tsx`:
  - Browser MediaRecorder → webm audio blob → POST to /api/voice
  - 4 pre-recorded Hindi command buttons for non-Hindi judges:
    - "▶️ Amul ka rate 32 karo"
    - "▶️ Atta khatam ho gaya"
    - "▶️ Maggi add karo, 14 rupees"
    - "▶️ Kitne products hain?"
  - Click button → sends pre-recorded audio to backend
- [ ] Build `AgentActivityPanel.tsx`:
  - Collapsible panel below chat
  - Shows: active agent, tools called, KB searches, memory events, latency, tokens
  - Real-time update from `agent_activity` field in API responses
  - Visual trace: Supervisor → [Agent Name] → [Tool Name] → result
- [ ] Build `BuyerCatalogView.tsx`:
  - Separate page/tab: `/catalog/{merchant_id}`
  - "Ramesh Ki Dukaan" header with shop details
  - Product grid with images, Hindi names, prices
  - Category filter tabs
  - ONDC badge: "ONDC Compliant ✅ | Powered by Vyapari.ai"
  - Mobile responsive
- [ ] Build `DemoGuide.tsx`:
  - Overlay shown on first visit:
  - "Welcome to Vyapari.ai 🙏 — Step 1: Tell us your shop name → Step 2: Upload shelf photo → Step 3: Try a Hindi voice command → Step 4: See your ONDC store!"
  - "Start Demo →" button dismisses overlay
- [ ] Connect all components to backend API (`services/api.ts`)
- [ ] Test on desktop Chrome, mobile Chrome, Safari

**Checkpoint:** Full web app working — judges can onboard, upload photos, use voice, see catalog, see orders.

### Phase 10: Frontend Deployment (Day 12)
- [ ] Build React app: `npm run build`
- [ ] Upload `dist/` to S3 bucket `vyapari-web`
- [ ] Create CloudFront distribution pointing to S3
- [ ] Configure CORS on API Gateway to allow CloudFront origin
- [ ] Test live URL end-to-end
- [ ] Optional: register vyapari.ai domain, point to CloudFront

**Checkpoint:** Live URL accessible by judges.

### Phase 11: API Layer (Day 12-13)
- [ ] Write `api/main.py` — FastAPI app with CORS, routes
- [ ] Write `api/routes/chat.py` — POST /api/chat → invoke AgentCore Runtime
- [ ] Write `api/routes/upload.py` — POST /api/upload → S3 upload + invoke Catalog Agent
- [ ] Write `api/routes/voice.py` — POST /api/voice → S3 upload + invoke Voice Agent
- [ ] Write `api/routes/catalog.py` — GET /api/catalog/{merchant_id} → DynamoDB query
- [ ] Write `api/services/agent_service.py`:
  - `invoke_agent(session_id, payload)` → boto3 InvokeAgentRuntime
  - Parse response, extract agent_activity metadata
  - Return structured ChatResponse
- [ ] Write `api/services/media_service.py`:
  - `upload_photo(file)` → S3, return key
  - `upload_voice(file)` → S3, return key
  - `get_presigned_url(key)` → S3 presigned URL for audio responses
- [ ] Deploy API: Lambda + API Gateway OR ECS/Fargate (choose based on latency needs — AgentCore calls can be long-running, Lambda 30s timeout may be tight)
- [ ] IMPORTANT: If using Lambda, set timeout to maximum (15 min for async) or use API Gateway WebSocket for streaming. Alternatively, use ECS Fargate for the API server.

**Checkpoint:** API layer connecting web frontend to AgentCore Runtime.

### Phase 12: Multilingual + Polish (Day 13-14)
- [ ] Write `agents/tools/translate_tools.py`:
  - `translate_text(text, source_lang, target_lang)` → Amazon Translate
- [ ] Add language detection to Supervisor: detect incoming message language
- [ ] Translate product descriptions: Hindi → Tamil, Telugu, Bengali (at least one additional language)
- [ ] Test: switch language to Tamil in frontend → bot greets in Tamil → product descriptions in Tamil
- [ ] Add Translate for voice: Polly supports Tamil (`voice_id: "Aditi"` for Hindi, use available Tamil/Telugu voice)
- [ ] Polish agent responses: make them warm, not robotic. Test with multiple conversation flows.
- [ ] Add error handling: graceful messages for failed photo analysis, voice not understood, etc.
- [ ] Cost guardrails: limit Bedrock calls per session (e.g., max 10 photos, max 20 voice commands)
- [ ] Performance optimization: identify and fix slow agent responses

**Checkpoint:** Multi-language support working. All edges smoothed.

### Phase 13: AgentCore Observability Setup (Day 14-15)
- [ ] Enable AgentCore Observability in CloudWatch:
  - Follow: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-observability.html
  - Enable Transaction Search in CloudWatch
- [ ] Verify traces appear: invoke agent → check CloudWatch for end-to-end trace
- [ ] Verify metrics: token usage, latency, session duration, error rates per agent
- [ ] Take screenshots of CloudWatch dashboards for blog post
- [ ] Ensure AgentActivityPanel in frontend shows real trace data (or closely mirrors it)
- [ ] Seed demo data: pre-create a "Ramesh" merchant with full catalog for demo recording

**Checkpoint:** Full observability configured. Demo data seeded.

### Phase 14: Twilio WhatsApp Sandbox + Video Recording (Day 15-16)
- [ ] Set up Twilio WhatsApp sandbox: register your phone number
- [ ] Create webhook endpoint that connects to same AgentCore backend
- [ ] Test full merchant journey on actual WhatsApp UI
- [ ] Write video script (see `docs/video-script.md`)
- [ ] Record video segments:
  - WhatsApp onboarding flow (screen record phone)
  - Photo upload + catalog generation (WhatsApp)
  - Voice command (WhatsApp voice note)
  - Order notification + savings (WhatsApp)
  - Buyer-side catalog view (phone browser)
  - Agent Activity Panel (web app — for "under the hood" segment)
  - Architecture diagram narration (screen share)
- [ ] Multiple takes per segment
- [ ] Add English subtitles for all Hindi content (CRITICAL for judges)

**Checkpoint:** All video segments recorded.

### Phase 15: Video Edit + Blog + Submission (Day 17-19)
- [ ] Edit video: combine segments, add transitions, subtitles, music, architecture overlays. Under 3 minutes.
- [ ] Upload video to YouTube (unlisted) or Google Drive
- [ ] Write technical blog on AWS Builder Center:
  - Title: "Building Agentic Commerce for Bharat with Amazon Bedrock AgentCore"
  - Sections: Problem, Multi-agent architecture, AgentCore Memory innovation, Multimodal KB, Demo results
  - Include architecture diagrams, code snippets, screenshots, CloudWatch dashboards
  - Publish and get link
- [ ] Clean up GitHub repo:
  - README with architecture diagram, setup instructions, tech stack, team info
  - Remove debug code, add code comments
  - Add LICENSE
  - Verify repo is public (or share with judges)
- [ ] Final submission:
  - PPT ✅ (update with Vyapari.ai branding if needed)
  - Video link
  - Live URL (CloudFront)
  - GitHub link
  - Blog link

**Checkpoint:** SUBMITTED ✅

---

## Agent System Prompts — Key Design Principles

### For ALL agents:
- Speak in Hindi (Devanagari script) by default. Mix English naturally where Indian merchants would ("product", "order", "price", "delivery" are fine in English)
- Be warm and respectful: use "ji" suffix ("Ramesh ji"), "aap" (formal you)
- Never expose internal agent names or architecture. Merchant sees ONE assistant: "Vyapari"
- Confirm before executing destructive actions (delete product, reject order)
- Include confidence levels internally for quality tracking

### For Supervisor specifically:
- NEVER say "Let me route you to the Catalog Agent." Instead: seamlessly hand off
- If uncertain about routing, default to asking a clarifying question
- Prioritize merchant's expressed intent over rigid flow
- Handle interruptions: merchant asks about orders mid-catalog-creation → Order Agent handles it, then return to Catalog Agent

---

## Coding Standards

### Python
- Python 3.10+ (AgentCore requirement)
- Type hints on all functions: `def save_merchant(data: MerchantData) -> str:`
- Pydantic v2 for all data models / API schemas
- Use `async/await` for all I/O operations (DynamoDB, S3, Bedrock, Transcribe, Polly)
- Logging with `structlog` or standard `logging` — structured JSON logs
- Environment variables for all config (never hardcode AWS credentials, table names, bucket names)
- Use `boto3` sessions with explicit region configuration

### TypeScript / React
- Functional components only, hooks for all state
- TailwindCSS utility classes — no custom CSS files
- TypeScript strict mode
- API calls in `services/api.ts` — never in components directly
- Component files: PascalCase (`ChatInterface.tsx`)
- Types in `types/index.ts`

### Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Branch: `main` (we're in hackathon mode, no feature branches needed)
- Meaningful commit messages: `feat: add catalog agent with KB integration`

---

## Testing Requirements

### For hackathon, focus on integration testing (not unit tests):
- [ ] Test each agent independently: send prompt → verify response format
- [ ] Test supervisor routing: verify each message type routes to correct agent
- [ ] Test full journey: onboard → catalog → voice → orders → buyer view
- [ ] Test with 5 different kirana shelf photos — verify reasonable catalog output
- [ ] Test with 5 different Hindi voice commands — verify correct intent detection
- [ ] Test KB search — verify uncertain products get KB matches
- [ ] Test memory persistence — verify merchant context survives session restart
- [ ] Test web app on Chrome + Safari + mobile Chrome
- [ ] Test API under load: 3 concurrent sessions (judges might test simultaneously)

### Test Commands
```bash
# Test individual agents
python scripts/test_agents.py --agent onboarding
python scripts/test_agents.py --agent catalog --photo tests/fixtures/sample_shelf_photos/snacks.jpg
python scripts/test_agents.py --agent voice --audio tests/fixtures/sample_voice_commands/price_update.webm
python scripts/test_agents.py --agent order --merchant_id <id>

# Test full journey
python scripts/test_agents.py --full-journey

# Seed demo data
python scripts/seed_demo_data.py

# Simulate orders
python scripts/simulate_orders.py --merchant_id <id> --count 5
```

---

## Do's and Don'ts

### ✅ Do
- Use AgentCore Memory for ALL state — don't build custom session management
- Use AgentCore Gateway for ALL tool access — don't have agents call boto3 directly
- Return `agent_activity` metadata in every API response — frontend needs it for Activity Panel
- Use streaming responses where possible (SSE) — makes the UX feel alive
- Include sample photos and pre-recorded voice commands — judges WILL need them
- Test on mobile — judges may open the URL on their phone
- Add a Reset button — judges need to start fresh
- Log everything — CloudWatch logs are your debugging lifeline
- Use `us-east-1` or `us-west-2` for AgentCore — verify regional availability before starting

### ❌ Don't
- Don't build a monolithic chatbot — the multi-agent architecture IS the innovation
- Don't skip the Knowledge Base — it's the visual product intelligence differentiator
- Don't hardcode any AWS credentials — use IAM roles and environment variables
- Don't expose agent internals to merchant — they see "Vyapari," not "Catalog Agent"
- Don't skip Hindi voice — even if Transcribe accuracy is imperfect, it shows the vision
- Don't over-optimize for edge cases — the demo needs to work for ONE happy path flawlessly
- Don't use `ap-south-1` for AgentCore if it's not available — deploy agents in available region, data in Mumbai
- Don't build real ONDC Beckn integration — simulated/mocked is fine. Schema compliance matters, live protocol doesn't.
- Don't spend time on auth — no login needed for hackathon
- Don't forget English subtitles in the video — judges may not read Hindi

---

## Environment Variables

```bash
# AWS
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# AgentCore
AGENTCORE_SUPERVISOR_ARN=arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:agent-runtime/XXXXX
AGENTCORE_MEMORY_ID=memory-XXXXX

# Bedrock
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514
BEDROCK_KB_ID=XXXXX

# DynamoDB Tables
DYNAMODB_MERCHANTS_TABLE=vyapari-merchants
DYNAMODB_PRODUCTS_TABLE=vyapari-products
DYNAMODB_ORDERS_TABLE=vyapari-orders
DYNAMODB_SESSIONS_TABLE=vyapari-sessions

# S3 Buckets
S3_PHOTOS_BUCKET=vyapari-photos
S3_PRODUCT_KB_BUCKET=vyapari-product-kb
S3_VOICE_BUCKET=vyapari-voice
S3_WEB_BUCKET=vyapari-web

# Transcribe
TRANSCRIBE_CUSTOM_VOCABULARY=vyapari-hindi-vocab
TRANSCRIBE_LANGUAGE=hi-IN

# Polly
POLLY_VOICE_ID=Aditi
POLLY_ENGINE=neural
POLLY_LANGUAGE=hi-IN

# Translate
TRANSLATE_SOURCE=hi
TRANSLATE_TARGETS=ta,te,bn,en

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://CLOUDFRONT_URL,http://localhost:5173

# CloudFront
CLOUDFRONT_DISTRIBUTION_ID=XXXXX
CLOUDFRONT_DOMAIN=dXXXXX.cloudfront.net
```

---

## References

### AWS Documentation (Bookmark These)
- [AgentCore Getting Started](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-toolkit.html)
- [AgentCore Runtime Python Deployment](https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/python/)
- [AgentCore Python SDK](https://github.com/aws/bedrock-agentcore-sdk-python)
- [AgentCore Starter Toolkit](https://pypi.org/project/bedrock-agentcore-starter-toolkit/)
- [Strands Agents Documentation](https://strandsagents.com/)
- [Bedrock Multimodal Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html)
- [Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal-create.html)
- [Amazon Transcribe Hindi](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html)
- [Amazon Polly Hindi Voice](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)
- [Bedrock Claude Sonnet 4 Multimodal](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html)
- [ONDC Beckn Protocol Spec](https://developers.becknprotocol.io/)

### Project Documents
- `ARCHITECTURE.md` — Detailed system architecture
- `docs/product-spec.md` — Full product specification
- `docs/merchant-scenarios.md` — 10 merchant scenario analyses
- `docs/competitive-analysis.md` — vs Blinkit, JioMart, Swiggy, Zepto
- `docs/video-script.md` — 3-minute video script
