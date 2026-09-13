# NEXOMATE Technical Architecture Document

**AI Lead Conversion System | v1.0 | Prepared for Founder’s Review**

---

## 1. EXECUTIVE SUMMARY

This document outlines the technical architecture for Nexomate’s AI-powered lead conversion platform. The system is designed to capture, qualify, score, and nurture inbound leads for solar installation and interior design companies across international markets.

**Core Principle:** Build once as a template, deploy per client with configuration — not custom code.

---

## 2. SYSTEM ARCHITECTURE (High-Level)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LEAD SOURCES                              │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────────────┤
│   Website   │  Facebook   │   Google    │  WhatsApp   │     Manual/CSV/     │
│    Forms    │  Lead Ads   │     Ads     │  Business   │     API Imports     │
│             │             │             │     API     │                     │
└──────┬──────┴──────┬──────┴──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │             │             │                 │
       └─────────────┴─────────────┴─────────────┴─────────────────┘
                                   │
                     ┌─────────────▼─────────────┐
                     │     N8N ORCHESTRATION     │
                     │  (Core Workflow Engine)   │
                     │ ┌───────────────────────┐ │
                     │ │ • Webhook Listener    │ │
                     │ │ • Lead Router         │ │
                     │ │ • AI Processing       │ │
                     │ │ • Scoring Engine      │ │
                     │ │ • Action Dispatcher   │ │
                     │ └───────────────────────┘ │
                     └─────────────┬─────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼───────┐          ┌────────▼────────┐          ┌───────▼───────┐
│   AI LAYER   │          │   CRM / DATA    │          │ COMMUNICATION │
│              │          │                 │          │               │
│ • OpenAI     │          │ • HubSpot / GHL │          │ • Twilio (SMS)│
│ • Claude 3.5 │          │ • Pipedrive     │          │ • SendGrid    │
│ (Qualify &   │          │ • PostgreSQL    │          │ • WhatsApp    │
│  Response)   │          │   (Audit Logs)  │          │   Business    │
└──────────────┘          └─────────────────┘          └───────────────┘
                                   │
                     ┌─────────────▼─────────────┐
                     │ SCHEDULING & APPOINTMENT  │
                     │   Calendly / SavvyCal     │
                     └───────────────────────────┘
```

---

## 3. N8N WORKFLOW ARCHITECTURE

### 3.1 Master Lead Processing Pipeline

```text
[Webhook Trigger] ──► [Lead Validation] ──► [Duplicate Check]
                                                   │
                                                   ▼
                                          [Language Detection]
                                                   │
                                    ┌──────────────┴──────────────┐
                                    ▼                             ▼
                              [English Path]               [Non-English Path]
                                    │                             │
                                    └──────────────┬──────────────┘
                                                   ▼
                                          [AI Response Node]
                                       (Instant Acknowledgment)
                                                   │
                                                   ▼
                                         [Qualification Node]
                                       (3-4 Dynamic Questions)
                                                   │
                                                   ▼
                                         [Lead Scoring Engine]
                                                   │
              ┌──────────────────┬─────────────────┼─────────────────┐
              ▼                  ▼                 ▼                 ▼
            [HOT]              [WARM]            [COLD]        [DISQUALIFIED]
              │                  │                 │                 │
              ▼                  ▼                 ▼                 ▼
      [Instant Booking      [Follow-Up         [Nurture          [Archive +
       Sales Sequence]       Sequence]           Tag]           Sales Alert]
              │                  │                 │                 │
              ▼                  ▼                 ▼                 ▼
         [CRM Update]       [CRM Update]      [CRM Update]      [CRM Update]
              │                  │                 │                 │
              └──────────────────┴─────────────────┴─────────────────┘
                                                   │
                                                   ▼
                                           [Audit Log Entry]
                                        (PostgreSQL / Airtable)
```

### 3.2 Follow-Up Sequence Engine (WARM Leads)

- **Day 0 (T+0 min):** AI Instant Response + Qualification
- **Day 0 (T+2 hrs):** Value-driven follow-up (if no reply)
- **Day 1 (T+24 hrs):** Case study / testimonial share
- **Day 3 (T+72 hrs):** Direct booking link + urgency
- **Day 7 (T+168 hrs):** Final attempt + long-term nurture tag

### 3.3 Nurture Sequence Engine (COLD Leads)

- **Week 1:** Educational content (solar ROI calculator, design trends)
- **Week 2:** Social proof (recent installations, client reviews)
- **Week 3:** Soft re-qualification ("Still considering solar?")
- **Week 4+:** Monthly newsletter automation

---

## 4. TECHNOLOGY STACK

| Layer | Primary Tool | Alternative | Justification |
|---|---|---|---|
| **Workflow Engine** | n8n (Self-hosted) | Make.com, Zapier | Full control, no per-task limits, custom nodes |
| **AI / LLM** | OpenAI GPT-4o | Claude 3.5 Sonnet, Gemini 1.5 | Best cost/performance for structured output |
| **CRM (Primary)** | GoHighLevel (GHL) | HubSpot, Pipedrive | Built-in SMS/email, popular in US solar market |
| **CRM (Enterprise)** | HubSpot | Salesforce | Better for larger international clients |
| **Database** | PostgreSQL (Supabase) | Airtable, MongoDB | Structured data, audit compliance, low cost |
| **Email** | SendGrid | Mailgun, AWS SES | Deliverability, templates, analytics |
| **SMS** | Twilio | MessageBird, Vonage | Global coverage, programmable |
| **WhatsApp** | WhatsApp Business API | 360dialog, WATI | Required for EU, LATAM, India, Middle East |
| **Scheduling** | SavvyCal | Calendly, Acuity | Better timezone handling, white-label |
| **Voice AI** | Bland AI / Retell | Vapi, Synthflow | Premium upsell — 3-5x conversion boost |
| **Hosting** | DigitalOcean / Hetzner | AWS, GCP | Cost-effective for early stage |
| **Monitoring** | n8n Error Workflows + Slack | Sentry, Datadog | Immediate failure alerts |
| **Secrets Mgmt** | n8n Built-in + .env | HashiCorp Vault | Sufficient for current scale |

---

## 5. DATA MODEL

### 5.1 Core Lead Entity

```sql
CREATE TABLE leads ( 
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    client_id UUID NOT NULL, 
    source VARCHAR(50) NOT NULL, -- website, facebook, google, whatsapp 
    source_detail VARCHAR(255),  -- specific campaign, page URL 

    -- Contact Info 
    first_name VARCHAR(100), 
    last_name VARCHAR(100), 
    email VARCHAR(255), 
    phone VARCHAR(50), 
    country_code VARCHAR(5),     -- +1, +44, +91, etc. 

    -- Qualification Data (JSONB for flexibility) 
    qualification_answers JSONB, 

    -- Scoring 
    lead_score VARCHAR(20) CHECK (lead_score IN ('HOT', 'WARM', 'COLD', 'DISQUALIFIED')), 
    score_reason TEXT, 

    -- Status Tracking 
    status VARCHAR(50) DEFAULT 'new', -- new, contacted, qualified, booked, converted, lost 
    ai_conversation_history JSONB,    -- Full chat log 

    -- Compliance 
    consent_given BOOLEAN DEFAULT FALSE, 
    consent_timestamp TIMESTAMPTZ, 
    gdpr_opt_in BOOLEAN DEFAULT FALSE, 

    -- Timestamps 
    created_at TIMESTAMPTZ DEFAULT NOW(), 
    updated_at TIMESTAMPTZ DEFAULT NOW(), 
    first_response_at TIMESTAMPTZ, 
    qualified_at TIMESTAMPTZ, 
    booked_at TIMESTAMPTZ 
); 

CREATE INDEX idx_leads_client_score ON leads(client_id, lead_score); 
CREATE INDEX idx_leads_created ON leads(created_at DESC); 
CREATE INDEX idx_leads_email ON leads(email); 
CREATE INDEX idx_leads_phone ON leads(phone); 
```

### 5.2 Client Configuration Entity

```sql
CREATE TABLE client_configs ( 
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
    client_name VARCHAR(255) NOT NULL, 
    industry VARCHAR(50) CHECK (industry IN ('solar', 'interior_design')), 

    -- AI Configuration 
    ai_prompt_system TEXT,         -- System prompt for this client 
    ai_temperature DECIMAL(3,2) DEFAULT 0.7, 
    qualification_questions JSONB, -- Array of question objects 

    -- Scoring Rules (JSONB) 
    scoring_rules JSONB, 
    
    -- Integration Settings 
    crm_type VARCHAR(50),          -- ghl, hubspot, pipedrive 
    crm_credentials_encrypted TEXT, 
    
    -- Communication Preferences 
    preferred_channels JSONB,      -- ["email", "sms", "whatsapp"] 
    business_hours JSONB,          -- {"monday": {"open": "09:00", "close": "18:00"}} 
    timezone VARCHAR(50) DEFAULT 'UTC', 
    
    -- Follow-up Configuration 
    follow_up_sequence JSONB,      -- Customizable per client 
    
    created_at TIMESTAMPTZ DEFAULT NOW(), 
    updated_at TIMESTAMPTZ DEFAULT NOW() 
); 
```

---

## 6. INTEGRATION MATRIX

### 6.1 Lead Sources → n8n

| Source | Integration Method | Trigger Type | Notes |
|---|---|---|---|
| **Website Forms** | n8n Webhook Node | HTTP POST | Embed webhook URL in form action |
| **Facebook Lead Ads** | Facebook Graph API | Polling (15 min) | Or Zapier bridge initially |
| **Google Ads** | Google Ads API | Webhook via Zapier | Leads directly to webhook |
| **WhatsApp** | WhatsApp Business API | Webhook | Meta Business verification required |
| **Phone Calls** | Twilio + AI Voice | Webhook | Premium feature |
| **Manual Import** | CSV Upload + n8n | Manual trigger | Bulk import workflow |

### 6.2 n8n → CRM

| CRM | API Method | n8n Node | Data Sync |
|---|---|---|---|
| **GoHighLevel** | REST API | HTTP Request | Contacts, Opportunities, Custom Fields |
| **HubSpot** | REST API | HubSpot Node | Contacts, Deals, Timeline Events |
| **Pipedrive** | REST API | Pipedrive Node | Persons, Deals, Activities |

### 6.3 n8n → Communication

| Channel | Provider | n8n Node | Template System |
|---|---|---|---|
| **Email** | SendGrid | SendGrid Node | Dynamic MJML templates |
| **SMS** | Twilio | Twilio Node | Per-client message variants |
| **WhatsApp** | WhatsApp Business API | HTTP Request | Template messages (Meta approved) |

---

## 7. AI PROMPT ARCHITECTURE

### 7.1 System Prompt Structure (Per Industry)

```text
You are [Client Name]'s AI Lead Assistant. Your job is to:

1. Respond instantly and warmly to new enquiries
2. Ask 3-4 qualification questions to understand the prospect
3. Score the lead as HOT, WARM, or COLD based on answers
4. Move HOT leads toward booking a consultation

INDUSTRY: Solar Installation

QUALIFICATION QUESTIONS:
1. What is your average monthly electricity bill?
2. Do you own your home? (Critical for solar)
3. Are you looking to install within the next 3 months?
4. What is your preferred contact method?

SCORING RULES:
- HOT: Owns home + bill > $150 + wants install within 3 months
- WARM: Owns home + interested but timeline unclear
- COLD: Renter, or just browsing, or timeline > 6 months

TONE: Professional, helpful, concise. Max 2-3 sentences per message.
LANGUAGE: Respond in the same language as the prospect's message.
```

### 7.2 Structured Output Format (JSON Mode)

```json
{ 
    "response_text": "Thank you for your interest in solar! To help us prepare the best recommendation, could you share your average monthly electricity bill?", 
    "lead_score": "WARM", 
    "score_reason": "Prospect owns home but timeline is unclear", 
    "next_action": "ask_qualification_question_2", 
    "language_detected": "en", 
    "sentiment": "positive" 
}
```

---

## 8. SECURITY & COMPLIANCE ARCHITECTURE

### 8.1 Data Protection by Region

| Regulation | Requirement | Implementation |
|---|---|---|
| **GDPR (EU/UK)** | Consent, Right to deletion, Data portability | Consent checkbox pre-capture; automated deletion workflow; data export endpoint |
| **CCPA (California)** | Opt-out, Disclosure | Unsubscribe link in all comms; privacy policy automation |
| **CAN-SPAM (US)** | Unsubscribe, Physical address | Footer in all emails; one-click unsubscribe |
| **CASL (Canada)** | Express consent | Double opt-in for Canadian leads |
| **LGPD (Brazil)** | Similar to GDPR | Apply GDPR workflow to Brazilian leads |

### 8.2 Security Measures

- **n8n Basic Auth + API Key Protection**
- **Webhook URL Signing (HMAC)**
- **Encrypted Credentials in n8n**
- **PostgreSQL Row-Level Security**
- **HTTPS Only (Let's Encrypt)**
- **Rate Limiting on Webhooks**
- **IP Whitelisting for Admin Access**
- **Regular Credential Rotation**

### 8.3 Consent Workflow

```text
       [Lead Enters]
             │
             ▼
      [Check Country/IP] ──► EU/UK/CA? ──► [Show Consent Banner]
             │                                     │
             ▼ (No)                                ▼
       [Proceed with                       [Capture Consent]
        Automation]                                │
             │                                     ▼
             │                            [Log Consent in DB]
             │                                     │
             └────────────────┬────────────────────┘
                              ▼
                 [GDPR Compliant Processing]
```

---

## 9. DEPLOYMENT ARCHITECTURE

### 9.1 Infrastructure Setup

```text
┌─────────────────────────────────────────────────────────────┐
│                 DIGITALOCEAN / HETZNER                      │
│                                                             │
│   Ubuntu 22.04 LTS Server                                   │
│                                                             │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│   │             │   │             │   │             │       │
│   │     N8N     │   │ PostgreSQL  │   │    Nginx    │       │
│   │   (Docker)  │   │   (Docker)  │   │   Reverse   │       │
│   │  Port 5678  │   │  Port 5432  │   │    Proxy    │       │
│   │             │   │             │   │    + SSL    │       │
│   └─────────────┘   └─────────────┘   └─────────────┘       │
│                                                             │
└─────────────────────────────┬───────────────────────────────┘
                              │
                      ┌───────┴───────┐
                      ▼               ▼
                [Cloudflare]     [Slack Alerts]
                (DNS + WAF)       (Monitoring)
```

### 9.2 Docker Compose Configuration

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "127.0.0.1:5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${DB_USER}
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD}
      - WEBHOOK_URL=https://n8n.nexomate.com/
    volumes:
      - ~/.n8n:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=nexomate
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - n8n

volumes:
  postgres_data:
```

---

## 10. MONITORING & OBSERVABILITY

### 10.1 Error Handling Workflow

```text
[Any Workflow Fails] 
         │ 
         ▼ 
 [n8n Error Trigger] 
         │ 
         ▼ 
[Capture Error Details] 
         │ 
         ▼ 
  [Send Slack Alert] 
 (Channel: #n8n-alerts) 
 (Content: Workflow Name, Error Message, Timestamp, Lead ID)
         │ 
         ▼ 
 [Log to PostgreSQL] 
 (Table: error_logs)
         │ 
         ▼ 
  [Escalation Rule] 
 (If 3+ errors in 10 min → Page on-call)
```

### 10.2 Key Metrics Dashboard

| Metric | Source | Alert Threshold |
|---|---|---|
| **Webhook Response Time** | n8n Logs | > 5 seconds |
| **AI API Failures** | OpenAI / Claude | > 5% error rate |
| **CRM Sync Failures** | n8n Error Node | Any failure |
| **Lead Processing Lag** | PostgreSQL | > 2 minutes |
| **Daily Lead Volume** | PostgreSQL | Drop > 50% |
| **Conversion Rate** | CRM | Client-specific |

---

## 11. MULTI-TENANCY & SCALABILITY

### 11.1 Template-Based Deployment

```text
┌──────────────────────────────────────────────────┐
│                NEXOMATE PLATFORM                 │
├──────────────────────────────────────────────────┤
│                  TEMPLATE LAYER                  │
│ ├─ Solar Lead Conversion Template                │
│ ├─ Interior Design Template                      │
│ └─ Generic Consultation Template                 │
├──────────────────────────────────────────────────┤
│               CLIENT CONFIG LAYER                │
│ ├─ Client A (Solar, Texas, English)              │
│ ├─ Client B (Solar, Spain, Spanish)              │
│ └─ Client C (Interior, UK, English)              │
├──────────────────────────────────────────────────┤
│              SHARED INFRASTRUCTURE               │
│ ├─ n8n Instance                                  │
│ ├─ PostgreSQL (schema-per-client)                │
│ └─ Shared AI/Comms APIs                          │
└──────────────────────────────────────────────────┘
```

### 11.2 Scaling Path

| Phase | Clients | Infrastructure | Cost / Month |
|---|---|---|---|
| **MVP** | 1–3 | Single DO droplet ($24) | ~$50–80 |
| **Growth** | 4–10 | Upgraded droplet + managed DB ($48) | ~$150–200 |
| **Scale** | 10–30 | Multiple n8n workers + load balancer ($120) | ~$400–600 |
| **Enterprise** | 30+ | Kubernetes cluster + dedicated AI infra | Custom |

---

## 12. COST ESTIMATION (Per Client, Monthly)

| Component | Tool | Cost (USD) |
|---|---|---|
| **n8n Hosting** | DigitalOcean | $12–24 (shared across clients) |
| **AI (OpenAI)** | GPT-4o | $20–50 (depends on lead volume) |
| **Email** | SendGrid | $19.95 (100k emails) |
| **SMS** | Twilio | $0.0075/msg (~$15–30) |
| **WhatsApp** | Meta API | $0.005–0.05/msg (~$10–20) |
| **CRM** | GoHighLevel | $97–297 (per client, passed through) |
| **Database** | Supabase | $25 (shared) |
| **Voice AI** | Bland AI | $0.09/min (~$20–50) |
| **Total Variable** | | **~$120–250 per client** |

> **Pricing Recommendation:** $1,500 setup + $500–800/month retainer = healthy margin.

---

## 13. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1–2)
- [x] Set up n8n + PostgreSQL infrastructure
- [x] Build core webhook ingestion pipeline
- [x] Integrate OpenAI for basic response generation
- [x] Connect first CRM (GoHighLevel)
- [x] Build email/SMS notification workflows

### Phase 2: Intelligence (Weeks 3–4)
- [ ] Implement qualification question engine
- [ ] Build scoring algorithm (HOT/WARM/COLD)
- [ ] Create follow-up sequence automation
- [ ] Add appointment booking integration
- [ ] Build error handling + monitoring

### Phase 3: Scale (Weeks 5–6)
- [ ] Create industry templates (Solar, Interior Design)
- [ ] Add multi-language support
- [ ] Implement GDPR/compliance workflows
- [ ] Build client onboarding automation
- [ ] Create internal reporting dashboard

### Phase 4: Premium (Weeks 7–8)
- [ ] Integrate AI Voice Calling (Bland AI)
- [ ] Add WhatsApp Business API
- [ ] Build review/referral post-sale automation
- [ ] Implement advanced analytics
- [ ] Prepare for second market entry

---

## 14. RISK MITIGATION

| Risk | Impact | Mitigation |
|---|---|---|
| **n8n workflow failure** | High | Error workflows, redundant triggers, manual fallback |
| **AI API rate limiting** | Medium | Retry logic, fallback to Claude, queue system |
| **CRM API changes** | Medium | Abstraction layer, version pinning |
| **Data breach** | Critical | Encryption, least-privilege access, regular audits |
| **Client churn** | Medium | Monthly value reports, optimization loops |
| **Founder dependency** | High | Document everything, build self-service onboarding |

---

## 15. DECISION LOG (For Wednesday Discussion)

| Decision Needed | Options | Recommendation |
|---|---|---|
| **Primary CRM** | GHL vs HubSpot vs Pipedrive | Start with GHL (solar market), offer HubSpot as enterprise upsell |
| **Hosting** | Self-hosted vs n8n Cloud | Self-hosted (cost + control), migrate to cloud if ops overhead grows |
| **AI Model** | GPT-4o vs Claude vs Gemini | GPT-4o primary, Claude fallback for complex reasoning |
| **Voice AI** | Phase 1 or later | Phase 2 — it’s a premium upsell, not MVP |
| **Multi-language** | Day 1 or later | Day 1 for Spanish (US + Spain solar market), others on demand |
| **Pricing Model** | Project vs Retainer | Hybrid: $1,500 setup + $500/month base + performance tiers |
| **First Market** | US vs UK vs Australia | US solar market — highest willingness to pay, English-speaking |

---

## 16. APPENDIX

### A. n8n Webhook Security

```javascript
// HMAC Signature Validation in n8n Function Node 
const crypto = require('crypto'); 
const secret = $env.WEBHOOK_SECRET; 
const signature = $input.first().json.headers['x-signature']; 
const payload = JSON.stringify($input.first().json.body); 

const expected = crypto 
  .createHmac('sha256', secret) 
  .update(payload) 
  .digest('hex'); 

if (signature !== expected) { 
  return [{ json: { error: 'Invalid signature' } }]; 
} 
return $input.all(); 
```

### B. AI Response Caching Strategy

- Cache common responses (business hours, location, basic pricing) for 1 hour
- Reduces AI API costs by ~30%
- Implemented via n8n IF node + PostgreSQL cache table

### C. Backup Strategy

- Daily automated PostgreSQL dumps to S3-compatible storage
- n8n workflow exports versioned in Git
- Recovery time objective: < 4 hours

---

**Document Version:** 1.0  
**Prepared By:** Technical Lead — Nexomate  
**Date:** August 2026  
**Next Review:** Post-MVP Launch  

> _“Build the system you’d want to maintain at 3 AM when a client’s pipeline breaks.”_
