<p align="center">
  <img src="https://d1reocdt7srokm.cloudfront.net/blog_04_architecture_diagram.png" alt="Vyapari.ai Architecture" width="800">
</p>

<h1 align="center">Vyapari.ai</h1>
<h3 align="center">AI Commerce Copilot for Bharat</h3>

<p align="center">
  Multi-agent system on Amazon Bedrock AgentCore that onboards India's 63 million merchants onto ONDC through Hindi conversation, template catalogs, and voice commands.
</p>

<p align="center">
  <a href="https://d1reocdt7srokm.cloudfront.net"><strong>Live Demo</strong></a> &nbsp;|&nbsp;
  <a href="https://d1reocdt7srokm.cloudfront.net/blog.html"><strong>Technical Blog</strong></a> &nbsp;|&nbsp;
  <a href="#architecture"><strong>Architecture</strong></a> &nbsp;|&nbsp;
  <a href="#quick-start"><strong>Quick Start</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AWS-Bedrock%20AgentCore-FF9900?style=flat-square&logo=amazon-aws" alt="AWS Bedrock AgentCore">
  <img src="https://img.shields.io/badge/Claude-Sonnet%204-6B4FBB?style=flat-square" alt="Claude Sonnet 4">
  <img src="https://img.shields.io/badge/ONDC-Beckn%20Protocol-00A86B?style=flat-square" alt="ONDC">
  <img src="https://img.shields.io/badge/Language-Hindi%20First-F97316?style=flat-square" alt="Hindi First">
  <img src="https://img.shields.io/badge/LOC-9%2C300%2B-blue?style=flat-square" alt="Lines of Code">
</p>

---

## The Problem

India's ONDC network aims to be the "UPI of commerce" — but only **15,000 of 63 million merchants** have onboarded. That's a **99.97% gap**.

Why? The onboarding requires English literacy, manual product cataloging (3,000+ items), understanding HSN codes and GST rates, and navigating complex web dashboards. For a kirana store owner who runs his business through WhatsApp voice notes, this is an insurmountable barrier.

## The Solution

Vyapari.ai is a **team of 5 AI agents** — not a chatbot — that handles the entire merchant journey through Hindi conversation:

| What | How | Result |
|------|-----|--------|
| **Registration** | 3-message Hindi conversation | Zero forms |
| **Catalog** | Template with 278 pre-built products | 15 min vs 15 hours |
| **Orders** | Auto-accept with fee transparency | 87.7% revenue retained |
| **Intelligence** | Daily morning brief with stock alerts | Actionable insights |
| **Voice** | Hindi ASR + TTS | Works like WhatsApp |

---

## Architecture

<a name="architecture"></a>

```
Merchant (Web/WhatsApp) → CloudFront → FastAPI → Supervisor Agent (AgentCore Runtime)
                                                      ├── Onboarding Agent (registration, slot-filling)
                                                      ├── Catalog Agent (template + photo → ONDC catalog)
                                                      ├── Order Agent (orders, savings, fulfillment)
                                                      ├── Intelligence Agent (briefs, forecasts, alerts)
                                                      └── Voice Agent (Transcribe → intent → route → Polly)
                                                              │
                                                  ┌───────────┼───────────┐
                                                  ▼           ▼           ▼
                                             AgentCore    AgentCore    AgentCore
                                             Memory       Gateway      Observability
                                                  │           │           │
                                                  ▼           ▼           ▼
                                            DynamoDB/S3  Bedrock/       CloudWatch
                                                         Transcribe/
                                                         Polly/Translate
```

### 16 AWS Services Used

| Category | Services |
|----------|----------|
| **AI/ML** | Bedrock AgentCore (Runtime + Memory + Gateway), Claude Sonnet 4, Nova Embeddings, Knowledge Base |
| **Voice** | Amazon Transcribe (Hindi ASR), Amazon Polly (Hindi TTS), Amazon Translate |
| **Data** | DynamoDB (4 tables), S3 (4 buckets), SQS |
| **Infra** | CloudFront, API Gateway, EC2, Lambda, CloudWatch |

### Why AgentCore (Not Lambda + Bedrock Direct)?

- **Persistent Memory**: STM + LTM + Episodic — merchant context survives across sessions
- **MCP Gateway**: All tool calls (DynamoDB, S3, Transcribe) through unified auth
- **Session Isolation**: No context bleed between merchants
- **Observability**: Every agent invocation traced in CloudWatch

---

## Key Innovation: Template Catalogs

Every kirana store in Delhi stocks the same ~500 products. Instead of making merchants **create** catalogs, we ask them to **confirm** pre-built templates:

```
Old: "Scan barcode → Enter name → Enter MRP → Select category → Repeat 3,000x" (15 hours)
New: "Amul Gold Milk stock hai?" → [Haan] → "Price?" → [₹32] → Next (15 minutes)
```

**278 curated products** across 4 store types (Kirana, Restaurant, Sweet Shop, Bakery), each with Hindi+English names, MRP, HSN code, GST rate, and ONDC category mapping.

---

## ONDC Fee Transparency

| Platform | Merchant Gets | Commission | On ₹374 Order |
|----------|:------------:|:----------:|:--------------:|
| **ONDC** | **87.7%** | 12.3% | **₹328** |
| Zomato | 72.0% | 28.0% | ₹269 |
| Swiggy | 65.0% | 35.0% | ₹243 |

**Merchant saves ₹85/order** → ₹4,250/day → **₹1.5 lakh/month** for 50 orders/day.

---

## Tech Stack

### Backend (Python 3.10+)
- **Strands Agents SDK** — Multi-agent orchestration
- **Bedrock AgentCore SDK** — Runtime deployment, memory, gateway
- **FastAPI** — REST API (9 endpoints)
- **boto3** — AWS services (DynamoDB, S3, Transcribe, Polly, Translate)
- **Pydantic v2** — Request/response validation

### Frontend (React 18 + TypeScript)
- **Vite** — Build tooling
- **TailwindCSS** — Styling
- **Framer Motion** — Animations
- **20 components**, 4,457 LOC

### AI/ML
- **Claude Sonnet 4** — All agent reasoning (multimodal + Hindi)
- **Amazon Transcribe** — Hindi speech-to-text
- **Amazon Polly** — Hindi text-to-speech (Aditi voice)
- **Amazon Translate** — Hindi ↔ Tamil/Telugu/Bengali/English

---

## Project Structure

```
vyapari-ai/
├── app.py                          # AgentCore Runtime entrypoint
├── agents/
│   ├── supervisor.py               # Routes to 5 specialist agents
│   ├── onboarding_agent.py         # Merchant registration
│   ├── catalog_agent.py            # Product catalog (template/photo/voice)
│   ├── order_agent.py              # ONDC order management
│   ├── intelligence_agent.py       # Business insights & forecasting
│   ├── voice_agent.py              # Hindi ASR/TTS/intent
│   ├── prompts/                    # System prompts (524 LOC)
│   └── tools/                      # 40+ agent tools (3,443 LOC)
│       ├── dynamodb_tools.py       # Merchant/product CRUD
│       ├── order_tools.py          # Order lifecycle
│       ├── intelligence_tools.py   # Morning brief, stock alerts
│       ├── bedrock_tools.py        # Multimodal photo analysis
│       ├── ondc_tools.py           # Beckn schema generation
│       ├── transcribe_tools.py     # Hindi ASR
│       ├── polly_tools.py          # Hindi TTS
│       └── translate_tools.py      # Multilingual
├── api/
│   ├── main.py                     # FastAPI app
│   ├── routes/                     # 9 API endpoints
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── upload.py               # POST /api/upload (photos)
│   │   ├── voice.py                # POST /api/voice
│   │   ├── catalog.py              # GET /api/catalog/{id}
│   │   ├── demo.py                 # Demo merchant endpoints
│   │   ├── simulate.py             # Order simulation
│   │   ├── template.py             # Template catalog
│   │   └── intelligence.py         # Business intelligence
│   └── services/
│       ├── agent_service.py        # AgentCore invocation
│       └── intelligence_service.py # Insight generation
├── frontend/
│   └── src/
│       ├── App.tsx                 # Main router
│       ├── components/             # 20 React components
│       │   ├── LandingPage.tsx     # Hindi hero landing
│       │   ├── ChatInterface.tsx   # WhatsApp-style chat
│       │   ├── TemplateCatalog.tsx  # Accordion catalog
│       │   ├── BuyerSimulator.tsx   # Buyer experience
│       │   ├── IntelligenceCard.tsx # Morning brief
│       │   └── ...
│       ├── services/api.ts         # HTTP client
│       └── types/index.ts          # TypeScript types
├── data/
│   └── vyapari_seed_db_v2.json    # 278 curated products
├── infrastructure/
│   ├── dynamodb_tables.py          # Table creation
│   └── cloudformation/template.yaml
└── scripts/
    ├── seed_demo_data.py           # Populate demo merchants
    └── test_agents.py              # Agent integration tests
```

**Total: ~9,300 lines of code** (4,857 Python + 4,457 TypeScript)

---

## Quick Start

<a name="quick-start"></a>

### Prerequisites
- Python 3.10+
- Node.js 18+
- AWS CLI v2 configured with us-east-1
- Bedrock model access: Claude Sonnet 4, Nova Embeddings

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_REPO/vyapari-ai.git
cd vyapari-ai

# Python backend
pip install uv
uv venv && source .venv/bin/activate
uv pip install -e .

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure AWS
```bash
cp .env.example .env
# Edit .env with your AWS credentials and resource ARNs
```

### 3. Create Infrastructure
```bash
python infrastructure/dynamodb_tables.py
python scripts/seed_demo_data.py
```

### 4. Deploy Agents to AgentCore
```bash
agentcore create    # Create agent runtime
agentcore configure # Set memory + gateway
agentcore deploy    # Deploy to AgentCore Runtime
```

### 5. Run Locally
```bash
# Terminal 1: Backend
uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 6. Open
Navigate to `http://localhost:5173` — select a store type and start chatting in Hindi.

---

## Demo Walkthrough

### 1. Onboard in Hindi
> Type: "Main Ramesh hoon, Lajpat Nagar mein kirana store hai"
>
> The Onboarding Agent extracts name, location, and store type — asks only for missing info.

### 2. Build Catalog from Template
> Type: "catalog banao" → Select "kirana" → 134 pre-built products appear
>
> Toggle products on/off, edit prices, hit "Go Live" — catalog is ONDC-ready.

### 3. Receive Orders
> Orders arrive from ONDC buyer apps (Paytm, Magicpin, Ola) with full fee transparency.
>
> Accept → see savings: "₹85 saved vs Swiggy on this order!"

### 4. Get Morning Brief
> Type: "morning brief"
>
> See yesterday's orders, revenue, stock alerts, festival demand forecasts, competitor pricing.

### 5. Voice Commands
> Click mic → speak in Hindi: "Amul ka rate 32 karo"
>
> Voice Agent transcribes → routes to Catalog Agent → price updated.

---

## Environment Variables

```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your_account_id

# AgentCore
AGENTCORE_SUPERVISOR_ARN=arn:aws:bedrock-agentcore:...
AGENTCORE_MEMORY_ID=memory-...

# Bedrock
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0

# DynamoDB Tables
DYNAMODB_MERCHANTS_TABLE=vyapari-merchants
DYNAMODB_PRODUCTS_TABLE=vyapari-products
DYNAMODB_ORDERS_TABLE=vyapari-orders
DYNAMODB_SESSIONS_TABLE=vyapari-sessions

# S3 Buckets
S3_PHOTOS_BUCKET=vyapari-photos-{account_id}
S3_VOICE_BUCKET=vyapari-voice-{account_id}
S3_WEB_BUCKET=vyapari-web-{account_id}
```

---

## Results

| Metric | Value |
|--------|-------|
| Store types | 4 (Kirana, Restaurant, Sweet Shop, Bakery) |
| Curated products | 278 |
| Onboarding messages | 3 (zero forms) |
| Catalog creation time | 15 minutes (vs 15 hours) |
| Revenue retained (ONDC) | 87.7% (vs 65% Swiggy) |
| Languages supported | Hindi, English, Tamil, Telugu |
| AWS services used | 16 |
| Total LOC | 9,300+ |

---

## Links

| Resource | URL |
|----------|-----|
| **Live Demo** | https://d1reocdt7srokm.cloudfront.net |
| **Technical Blog** | https://d1reocdt7srokm.cloudfront.net/blog.html |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## Built With

<p align="center">
  <img src="https://img.shields.io/badge/Amazon_Bedrock-AgentCore-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="Bedrock AgentCore">
  <img src="https://img.shields.io/badge/Claude-Sonnet_4-6B4FBB?style=for-the-badge" alt="Claude">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/ONDC-Beckn_Protocol-00A86B?style=for-the-badge" alt="ONDC">
</p>

---

## Team

**Vikas Goel** — CTO, Nexvia.ai
- 28+ years in AI and telecom
- Building voice AI systems for India's next billion users

---

## License

MIT

---

<p align="center">
  <strong>आपकी दुकान। आपका नाम। अब पूरे भारत में।</strong><br>
  <em>Your shop. Your name. Now across all of India.</em>
</p>

<p align="center">
  Built for <strong>AWS AI for Bharat Hackathon 2026</strong> — Professional Track
</p>
