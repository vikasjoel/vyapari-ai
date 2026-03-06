# Building an AI Commerce Copilot for India's 63 Million Merchants with Amazon Bedrock AgentCore

**How Vyapari.ai uses multi-agent orchestration, template catalogs, and ONDC integration to onboard merchants in Hindi**

*By Vikas Goel, CTO at Nexvia.ai*

---

## The 99.97% Problem

India's Open Network for Digital Commerce (ONDC) represents one of the most ambitious digital public infrastructure projects in history. Designed as the "UPI of commerce," ONDC aims to democratize e-commerce by creating an open, decentralized network where any seller can reach any buyer through any participating app. The total addressable market? India's 63 million micro, small, and medium enterprises (MSMEs) — the kirana stores, restaurants, sweet shops, and bakeries that form the backbone of India's retail economy.

Yet as of early 2026, fewer than 15,000 merchants have successfully onboarded onto ONDC. That's a 99.97% gap between potential and reality.

The root causes are structural, not motivational. The typical ONDC onboarding flow requires merchants to:
1. Navigate English-language seller dashboards (65% of Indian merchants are more comfortable in regional languages)
2. Manually catalog every product — often 3,000 to 5,000 items — by scanning barcodes or typing SKU details
3. Understand complex commission structures, HSN codes, GST rates, and Beckn protocol schemas
4. Complete KYC verification through unfamiliar digital workflows

For a 45-year-old kirana owner in Lajpat Nagar who runs his business through WhatsApp voice notes and handwritten ledgers, this is an insurmountable barrier. Existing tools like Seller.ondc.org and MyStore require literacy in English and comfort with web applications — precisely what the "next half billion" lack.

**The merchant we're building for speaks Hindi, runs a physical store, owns a smartphone, and lives inside WhatsApp.** ONDC's promise of fair, decentralized commerce will remain unfulfilled unless we meet merchants where they are.

![Landing Page](blog_01_landing_page.png)
*Vyapari.ai landing page with Hindi hero text and 4 store types*

---

## The Template Catalog Insight: Know Your Merchant

The breakthrough came from a simple observation: **every kirana store in Delhi stocks the same 500 products.**

Walk into any neighborhood grocery store from Lajpat Nagar to Dwarka, and you'll find Amul Gold Milk (₹32 for 500ml), Britannia Good Day biscuits (₹35 for 200g), Tata Salt (₹22 for 1kg), and Maggi noodles (₹14 for 70g). Brand preference varies by income bracket and geography, but the core SKU universe is remarkably consistent.

This insight transforms the onboarding problem. Instead of asking a merchant to **create** a catalog from scratch, we can ask them to **confirm** a pre-built template. The interaction shifts from:

**Old way:**
*"Scan this barcode. Enter product name. Enter MRP. Select category. Enter HSN code. Choose GST rate. Repeat 3,000 times."*

**New way:**
*"Does your store stock Amul Gold Milk?" → [Yes] → "Price?" → [₹32] → Next product.*

We built **278 curated products** across 4 store types:
- **Kirana (134 items)**: Dairy, staples, snacks, beverages, personal care, household
- **Restaurant (73 items)**: North Indian, South Indian, Chinese, beverages, desserts
- **Sweet Shop (51 items)**: Traditional sweets, namkeen, festive specials
- **Bakery (20 items)**: Breads, cakes, pastries, cookies

Each product includes:
- Hindi + English names (e.g., "अमूल गोल्ड दूध" / "Amul Gold Milk")
- Accurate MRP (updated quarterly from GS1 India data)
- HSN code + GST rate (auto-calculated for ONDC schema)
- ONDC category mapping (e.g., "Dairy & Cheese" → `ONDC:F&B-1001`)
- Barcode/EAN (for future scan-to-confirm flows)

**Result:** A merchant can catalog 80 products in 15 minutes instead of 15 hours. This single innovation unlocks ONDC for thousands of merchants who would otherwise never complete onboarding.

![Template Catalog](blog_06_template_catalog.png)
*Template catalog with 134 products across 9 categories — merchant selects instead of creating*

---

## Architecture: Multi-Agent Orchestration on Bedrock AgentCore

Vyapari.ai is not a chatbot calling APIs. It's a **team of specialist AI agents** coordinated by a supervisor — each with distinct capabilities, persistent memory, and access to external tools.

### Why Multi-Agent?

The merchant journey requires fundamentally different cognitive skills:
- **Conversational extraction** (onboarding): Slot-filling from unstructured Hindi text
- **Visual analysis** (catalog): Multimodal understanding of shelf photos
- **Structured reasoning** (orders): Fee calculations, ONDC protocol compliance
- **Time-series analysis** (intelligence): Demand forecasting, stock trend detection

A single monolithic LLM would excel at none of these. By decomposing the problem into specialist agents, we achieve:
1. **Better accuracy** (each agent optimized for one task)
2. **Parallel execution** (catalog + order agents run concurrently)
3. **Independent evolution** (update onboarding logic without touching order agent)
4. **Observability** (trace which agent handled which turn)

### The Agent System

**Supervisor Agent** routes every merchant message to the appropriate specialist:

```python
from strands import Agent, tool
from agents.onboarding_agent import create_onboarding_agent
from agents.catalog_agent import create_catalog_agent
from agents.order_agent import create_order_agent
from agents.intelligence_agent import create_intelligence_agent

def create_supervisor_agent() -> Agent:
    onboarding_agent = create_onboarding_agent()
    catalog_agent = create_catalog_agent()
    order_agent = create_order_agent()
    intelligence_agent = create_intelligence_agent()

    @tool
    def handle_onboarding(message: str) -> str:
        """Route to onboarding specialist for registration."""
        result = onboarding_agent(message)
        return result.message

    @tool
    def handle_catalog(message: str) -> str:
        """Route to catalog specialist for product management."""
        result = catalog_agent(message)
        return result.message

    # ... similar tools for order and intelligence agents

    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-east-1"
    )

    return Agent(
        model=model,
        system_prompt=SUPERVISOR_PROMPT,
        tools=[handle_onboarding, handle_catalog, handle_orders, handle_intelligence]
    )
```

The supervisor maintains **no domain logic** — it's purely a router. This keeps reasoning chains short (1-2 LLM calls instead of 10+) and makes debugging tractable.

![Architecture Diagram](blog_04_architecture_diagram.png)
*Multi-agent system architecture on Amazon Bedrock AgentCore — 16 AWS services*

### Amazon Bedrock AgentCore: The Runtime Layer

We deploy all agents on **Bedrock AgentCore Runtime** — AWS's production-grade platform for multi-agent systems. AgentCore provides:

**1. Persistent Memory (STM + LTM + Episodic)**
Each merchant session has short-term memory (conversation context), long-term memory (profile data), and episodic memory (past interactions). When a merchant returns after 3 days, the system remembers:
- Their product catalog
- Previous orders
- Stock level alerts
- Preferred communication style (voice vs. text)

**2. AgentCore Gateway (MCP Server)**
All external tool calls — DynamoDB reads, S3 uploads, Transcribe jobs, Polly synthesis — route through the Gateway. This provides:
- Unified authentication (no credentials in agent code)
- Rate limiting + cost controls
- Audit logs for every tool invocation

**3. AgentCore Observability**
Every agent invocation publishes structured traces to CloudWatch:
```json
{
  "session_id": "abc-123",
  "supervisor_routed_to": "catalog_agent",
  "tools_called": ["analyze_photo", "update_product"],
  "latency_ms": 2340,
  "tokens_used": 856,
  "success": true
}
```

For the hackathon demo, we expose this in the **Agent Activity Panel** — judges can watch the multi-agent choreography in real-time.

![Agent Activity](blog_08_agent_activity.png)
*Real-time agent activity trace showing routing and latency metrics*

### Claude Sonnet 4 on Bedrock

We use **Claude Sonnet 4** (`us.anthropic.claude-sonnet-4-20250514-v1:0`) for all agents. Key capabilities:
- **Multimodal vision**: Analyze shelf photos, extract product details
- **Structured output**: Return valid JSON for ONDC Beckn schemas
- **Hindi understanding**: Correctly parse Devanagari text, handle code-switching
- **Long context**: 200k token window for full conversation history + template catalog

We considered other models (GPT-4, Gemini Pro, Mistral) but Sonnet 4's combination of multimodal quality + structured output + Hindi proficiency was unmatched.

---

## ONDC Integration: Transparent Commerce

ONDC's value proposition hinges on **fee transparency**. Unlike Swiggy or Zomato, where the commission structure is opaque and one-sided, ONDC decomposes every rupee:

### Fee Structure Breakdown

For a ₹374 grocery order on ONDC:
- **Buyer app fee** (Paytm/Magicpin): ₹8 (2.1%)
- **Seller app fee** (Vyapari.ai): ₹4 (1.0%)
- **Network fee** (ONDC protocol): ₹2 (0.5%)
- **Logistics** (Shadowfax/Dunzo): ₹25 (6.7%)
- **GST** on fees: ₹7 (18% on fees)

**Merchant receives:** ₹328 (87.7% of order value)

Compare this to traditional aggregators:
- **Swiggy**: ₹374 - ₹131 (35% commission) = ₹243 (65%)
- **Zomato**: ₹374 - ₹105 (28% commission) = ₹269 (72%)

**The merchant saves ₹85 per order.** For a restaurant doing 50 orders/day, that's ₹4,250/day or ₹1.5 lakh/month in retained earnings.

![Fee Comparison](blog_05_fee_comparison.png)
*ONDC fee transparency: 87.7% to merchant vs 65% on Swiggy*

### Beckn Protocol Compliance

ONDC uses the [Beckn protocol](https://becknprotocol.io/) — an open API specification for decentralized commerce. Vyapari.ai auto-generates compliant catalog descriptors:

```json
{
  "descriptor": {
    "name": "Amul Gold Milk",
    "short_desc": "Full Cream Milk",
    "long_desc": "Amul Gold Homogenised Toned Milk with 4.5% fat",
    "images": ["https://s3.../amul-gold-500ml.jpg"]
  },
  "price": {
    "currency": "INR",
    "value": "32.00",
    "maximum_value": "35.00"
  },
  "category_id": "Dairy & Cheese",
  "location_id": "delhi-lajpat-nagar",
  "@ondc/org/statutory_reqs_packaged_commodities": {
    "manufacturer_or_packer_name": "Amul",
    "manufacturer_or_packer_address": "Anand, Gujarat",
    "common_or_generic_name_of_commodity": "Milk",
    "month_year_of_manufacture_packing_import": "03/2026"
  },
  "@ondc/org/mandatory_reqs_veggies_fruits": {
    "net_quantity": "500ml"
  }
}
```

Merchants never see this complexity — Vyapari.ai handles schema generation, validation, and ONDC network registration.

---

## Intelligence Agent: Daily Value Beyond Transactions

Most seller platforms are **transactional** — they help you list products and fulfill orders. Vyapari.ai is **conversational** — it becomes the merchant's daily advisor.

The **Intelligence Agent** generates a morning brief every day:

### Example: Morning Brief for Ramesh General Store (March 6, 2026)

**🌅 नमस्ते रमेश जी! आज 6 मार्च, गुरुवार**

**📊 कल का बिजनेस (5 मार्च):**
- Orders: 8 (↑ 2 from avg)
- Revenue: ₹2,450
- Amount received: ₹2,143 (87.5%)
- ONDC fees: ₹307 (vs ₹857 on Swiggy — you saved ₹550!)

**⚠️ स्टॉक अलर्ट:**
- 🥛 Amul Gold Milk — 3 liters बचे हैं (restock today)
- 🍪 Parle-G Biscuits — कल 12 packets बिके (high demand, order more)

**📈 डिमांड फोरकास्ट:**
- 🎨 **Holi is tomorrow!** Colors, sweets, namkeen की demand 3x बढ़ेगी
- Suggested stock: Haldiram Bhujia (+20 packs), MDH Holi Colors (+50 packets)

**💡 सुझाव:**
- Your top seller: Bingo Chips (₹420 revenue yesterday) — restock now
- Competitor alert: Store 800m away reduced Maggi price to ₹13 (yours: ₹14)

![Morning Brief](blog_07_morning_brief.png)
*Daily intelligence brief with stock alerts and demand forecasting*

This intelligence comes from:
1. **Order history analysis** (DynamoDB time-series queries)
2. **Festive calendar awareness** (Holi, Diwali, Navratri, Eid)
3. **Simulated price comparison** (in production, scrape ONDC network data)
4. **Stock velocity trends** (detect fast-moving vs. slow-moving items)

For the hackathon, this is **rule-based + simulated**. But the architecture supports real ML integration — Amazon Forecast for demand prediction, SageMaker for price optimization, Bedrock Knowledge Base for competitive intelligence.

---

## AWS Services: The Full Stack

Vyapari.ai uses **16 AWS services** across compute, AI/ML, storage, and observability:

| Service | Role | Why This Matters |
|---------|------|------------------|
| **Bedrock AgentCore** | Multi-agent runtime, memory, gateway, observability | Production-grade agent orchestration without custom infra |
| **Bedrock (Claude Sonnet 4)** | LLM for all agents | Best multimodal + structured output + Hindi support |
| **Bedrock Knowledge Base** | Product visual similarity search (future) | Fill gaps when vision model uncertain |
| **Nova Multimodal Embeddings** | Vector search for product images | Match shelf photos to catalog |
| **Amazon Transcribe** | Hindi speech-to-text | Voice onboarding + product commands |
| **Amazon Polly** | Hindi text-to-speech (Aditi voice) | Voice responses for low-literacy merchants |
| **Amazon Translate** | Multilingual support | Expand to Tamil, Telugu, Bengali |
| **DynamoDB** | Merchants, products, orders, sessions | Single-digit ms reads for real-time catalog |
| **S3** | Photos, voice recordings, product images | Durable storage + presigned URLs |
| **CloudFront** | Frontend CDN | < 100ms latency globally |
| **Lambda** | API handlers, tool implementations | Serverless, auto-scaling |
| **API Gateway** | REST API for web frontend | CORS, throttling, API keys |
| **CloudWatch** | Logs, metrics, agent traces | Full observability |
| **EC2** | Backend API server (FastAPI) | Long-running agent connections |
| **SQS** | Async photo/voice processing | Decouple uploads from analysis |
| **Cognito** | User auth (future) | Secure merchant accounts |

The key architectural decision was **Bedrock AgentCore**. We could have built custom orchestration with Step Functions + Lambda, but AgentCore gives us:
- Built-in memory management (no DynamoDB session table hacks)
- Standardized tool interface (MCP protocol)
- CloudWatch integration (no custom logging)
- Session isolation (no context bleed between merchants)

This is **infrastructure as intelligence** — AWS handling the undifferentiated heavy lifting so we focus on agent logic.

---

## Results & What's Next

**What We Built (3 Days):**
- 4 store types with 278 curated products
- 3-message onboarding (zero forms, pure conversation)
- 15-minute catalog creation (vs. 15 hours manual)
- 87.7% merchant revenue retention (vs. 65% on Swiggy)
- Real-time fee transparency + order management
- Daily intelligence briefs with stock alerts + demand forecasts

**Live Demo:** [https://d1reocdt7srokm.cloudfront.net](https://d1reocdt7srokm.cloudfront.net)

![Chat Conversation](blog_03_chat_conversation.png)
*Hindi conversational onboarding — 3 messages to register a merchant on ONDC*

**What's Next:**

1. **GS1 India Integration**
   Connect to GS1's barcode database — merchants scan a product, we pull verified MRP, HSN code, and ONDC category.

2. **WhatsApp Business API**
   The web app is for judges. Production deployment lives inside WhatsApp — where 500M+ Indians already transact.

3. **Real ONDC Sandbox**
   Integrate with ONDC's staging network for end-to-end order fulfillment (currently simulated).

4. **Multimodal Knowledge Base**
   2,000+ product images with Nova embeddings — visual search for products not in templates.

5. **Regional Language Expansion**
   Tamil (9 crore speakers), Telugu (8 crore), Bengali (10 crore), Marathi (8 crore).

---

## The Vision: AI for Every Merchant in Bharat

ONDC's promise — fair, open, decentralized commerce — cannot be realized without merchant-side tooling that meets merchants where they are. Vyapari.ai proves that **conversational AI, template catalogs, and fee transparency** can unlock ONDC for the "next 63 million."

This isn't just about technology. It's about ensuring that the kirana owner in Lajpat Nagar, the dhaba operator in Ludhiana, and the sweet shop in Chennai can participate in India's digital economy — in their language, on their terms, with their data.

**Aapki dukaan. Aapka naam. Ab poore Bharat mein.**

---

## Try It Yourself

**Live Demo:** [https://d1reocdt7srokm.cloudfront.net](https://d1reocdt7srokm.cloudfront.net)
**GitHub:** [Coming Soon]
**Contact:** [Your Email]

*Built for AWS AI for Bharat Hackathon 2026 — Professional Track*

---

**About the Author**
Vikas Goel is CTO at Nexvia.ai, building voice AI systems for India's next billion users. He holds 28+ years of experience in AI and telecom, with production deployments serving millions of daily interactions. This is his first ONDC project, but not his last.

---

**Acknowledgments**
Thank you to the AWS Bedrock AgentCore team for early access to the platform, the ONDC team for documentation support, and the hundreds of kirana owners who shared their onboarding pain points during user research.
