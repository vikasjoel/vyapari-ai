# Vyapari.ai — 3-Minute Demo Video Script

> **Total Duration:** 2:55 (under 3 minutes)
> **Format:** Screen recording + voiceover (English narration with Hindi demo)
> **Tools:** Screen recording (OBS/QuickTime), phone screen mirror for WhatsApp segment
> **Resolution:** 1920x1080 (16:9)

---

## PRE-RECORDING CHECKLIST

- [ ] Open https://d1reocdt7srokm.cloudfront.net in Chrome (incognito, desktop)
- [ ] Clear any existing chat sessions (click Reset if available)
- [ ] Open a second browser tab for the buyer simulator
- [ ] Have phone ready for WhatsApp segment (optional)
- [ ] Test mic levels for voiceover
- [ ] Close all notifications and unrelated tabs

---

## SHOT LIST

### SHOT 1: Title Card (0:00 – 0:10) — 10 seconds

**Visual:** Animated title card (use pitch.html slide 1, or create in Canva)
```
Vyapari.ai
AI Commerce Copilot for Bharat
---
AWS AI for Bharat Hackathon 2026
Professional Track
```

**Voiceover:**
> "India has 63 million small merchants — but only 15,000 are on ONDC. That's a 99.97% gap. Vyapari.ai closes it with AI agents that speak Hindi."

---

### SHOT 2: The Problem (0:10 – 0:25) — 15 seconds

**Visual:** Show the landing page hero section with the Hindi stats:
- "1.3 करोड़ दुकान. सिर्फ 15,000 ONDC पे. हम यह बदलेंगे."
- Slowly scroll to show the 4 store type cards (Kirana, Restaurant, Sweet Shop, Bakery)

**Voiceover:**
> "The typical ONDC onboarding requires English literacy, manual cataloging of thousands of products, and understanding HSN codes. Our target merchant speaks Hindi, runs a physical store, and lives inside WhatsApp. We built a team of 5 AI agents — not a chatbot — that handles the entire journey through conversation."

---

### SHOT 3: Select Store Type (0:25 – 0:35) — 10 seconds

**Visual:**
- Click "Kirana Store" card on landing page
- Page transitions to the chat interface
- Bot greets in Hindi

**Voiceover:**
> "Let's onboard Ramesh, a kirana store owner in Lajpat Nagar, Delhi. He selects his store type and the Onboarding Agent takes over."

---

### SHOT 4: Hindi Onboarding — 3 Messages (0:35 – 1:05) — 30 seconds

**Visual:** Type these messages in the chat, pausing to show each bot response:

1. **User types:** `Main Ramesh Kumar hoon, Lajpat Nagar mein kirana store hai`
   - **Bot responds:** Extracts name, location, store type. Asks for shop name and phone.

2. **User types:** `Ramesh General Store, 9876543210`
   - **Bot responds:** Confirms registration, shows Merchant ID, suggests "Ab catalog banao"

**Action:** Show the Agent Activity panel briefly (click the toggle) — highlight "Supervisor → Onboarding Agent → save_merchant"

**Voiceover:**
> "Three messages. No forms. The Onboarding Agent extracts name, location, and store type from natural Hindi conversation — asks only for what's missing. Here in the agent activity panel, you can see the Supervisor routing to the Onboarding Agent, which calls the save_merchant tool to store Ramesh's profile in DynamoDB."

---

### SHOT 5: Template Catalog (1:05 – 1:35) — 30 seconds

**Visual:**
1. **User types:** `catalog banao`
2. Bot shows template catalog UI with 134 kirana products
3. **Scroll through categories** — show Dairy, Staples, Snacks accordion sections
4. Toggle a few products ON/OFF
5. Edit a price (change Amul Milk from ₹32 to ₹34)
6. Show the running counter: "87 / 134 products selected"
7. **Click "Go Live on ONDC"** — show confetti animation

**Voiceover:**
> "Here's our key innovation: template catalogs. Every kirana store stocks the same 500 products. Instead of making Ramesh create a catalog from scratch — which takes 15 hours — we ask him to confirm a pre-built template. 278 curated products with Hindi names, MRP, HSN codes, and ONDC category mappings. He toggles products on or off, edits prices, and goes live in 15 minutes. Watch — 134 products cataloged, and he's now an ONDC seller."

---

### SHOT 6: ONDC Order with Fee Savings (1:35 – 1:55) — 20 seconds

**Visual:**
1. An order notification appears in chat (from buyer app like Paytm)
2. Show the order details: items, total ₹374
3. Show the ONDC fee breakdown card:
   - Merchant receives: ₹328 (87.7%)
   - ONDC fees: ₹46
   - "vs Swiggy: ₹243 (65%) — You save ₹85!"
4. Click "Accept Order"

**Voiceover:**
> "An order arrives from Paytm via ONDC. On a 374 rupee order, Ramesh keeps 328 rupees — that's 87.7%. On Swiggy, he'd keep only 243. That's 85 rupees saved per order. For 50 orders a day, that's 1.5 lakh per month in retained earnings. This is why ONDC matters."

---

### SHOT 7: Morning Brief — Intelligence Agent (1:55 – 2:15) — 20 seconds

**Visual:**
1. **User types:** `morning brief`
2. Intelligence card appears showing:
   - Yesterday's stats (orders, revenue, amount received)
   - Stock alerts (Amul Milk running low)
   - Demand forecast (Holi tomorrow — stock sweets)
   - Suggestions (top seller, competitor pricing)

**Voiceover:**
> "Every morning, the Intelligence Agent delivers a brief in Hindi — yesterday's revenue, stock alerts, and demand forecasts. It knows Holi is tomorrow and suggests stocking extra sweets. This turns Vyapari from a transaction tool into a daily business advisor."

---

### SHOT 8: Architecture Overview (2:15 – 2:40) — 25 seconds

**Visual:** Show the architecture diagram (blog_04_architecture_diagram.png) or the pitch deck architecture slide. Highlight each layer as you narrate:
1. Merchant layer (Web/WhatsApp)
2. Supervisor Agent routing
3. 5 specialist agents
4. AgentCore Runtime, Memory, Gateway, Observability
5. 16 AWS services

**Voiceover:**
> "Under the hood: 5 specialist agents on Amazon Bedrock AgentCore Runtime — each with persistent memory, tool access through MCP Gateway, and full observability. The Supervisor routes every message to the right specialist. Claude Sonnet 4 powers all reasoning — multimodal vision for photos, structured output for ONDC schemas, and native Hindi understanding. 16 AWS services, 9,300 lines of code, all production-ready."

---

### SHOT 9: Closing — Vision + CTA (2:40 – 2:55) — 15 seconds

**Visual:** Show the landing page hero one more time, or the pitch deck final slide with:
```
आपकी दुकान। आपका नाम। अब पूरे भारत में।
Your shop. Your name. Now across all of India.
```

**Voiceover:**
> "Vyapari.ai — an AI Commerce Copilot for Bharat. Template catalogs, Hindi conversation, fair ONDC fees. 63 million merchants. Let's bring them online. Aapki dukaan. Aapka naam. Ab poore Bharat mein."

---

## RECORDING TIPS

### Voiceover
- Speak clearly and at moderate pace
- Emphasize key numbers: "99.97%", "15 minutes vs 15 hours", "87.7%", "₹85 saved"
- Use natural enthusiasm, not salesy
- Hindi pronunciation should be natural (you're native)

### Screen Recording
- Use 1920x1080 resolution
- Zoom browser to 110% for larger text
- Use smooth, deliberate mouse movements
- Pause 1-2 seconds on important UI elements
- If chat responses are slow (>5s), edit in post to speed up wait time

### Editing
- Add subtle background music (upbeat, low volume)
- Add English subtitles for ALL Hindi text on screen
- Add text annotations pointing to key features:
  - "5 AI Agents" when showing architecture
  - "278 Products" when showing template
  - "87.7% to Merchant" when showing fee breakdown
- Smooth transitions between shots (crossfade, 0.5s)
- Add lower-third: "Vikas Goel | CTO, Nexvia.ai" on closing shot

### Timing Guide
| Shot | Duration | Cumulative |
|------|----------|------------|
| 1. Title Card | 10s | 0:10 |
| 2. Problem | 15s | 0:25 |
| 3. Store Selection | 10s | 0:35 |
| 4. Onboarding | 30s | 1:05 |
| 5. Template Catalog | 30s | 1:35 |
| 6. ONDC Order | 20s | 1:55 |
| 7. Morning Brief | 20s | 2:15 |
| 8. Architecture | 25s | 2:40 |
| 9. Closing | 15s | 2:55 |

**Total: 2 minutes 55 seconds**

---

## POST-RECORDING

- [ ] Edit video (transitions, subtitles, annotations)
- [ ] Export as MP4 (H.264, 1080p, 30fps)
- [ ] Upload to YouTube (unlisted) or Google Drive
- [ ] Test link works (share with a friend)
- [ ] Add video link to hackathon submission

---

## ALTERNATIVE: CONDENSED 2-MINUTE VERSION

If you need to cut to 2 minutes, remove:
- Shot 2 (The Problem) — merge key stats into Shot 1
- Shot 8 (Architecture) — condense to 10 seconds showing just the diagram
- Shorten Shot 5 (Template Catalog) to 20 seconds

This gives approximately: 10 + 10 + 25 + 20 + 20 + 20 + 10 + 10 = 2:05
