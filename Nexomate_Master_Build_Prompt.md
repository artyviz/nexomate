# MASTER BUILD PROMPT — NEXOMATE MVP

## 0. ROLE

You are a senior full-stack engineer, Python engineer, automation engineer, and UI/UX designer.

Build a **fully functional local/self-hosted MVP of Nexomate**, not a mockup or static prototype.

The system must actually:

1. Analyze a client's business.
2. Define/find its ideal customer profile.
3. Discover potential prospects.
4. Collect structured lead information.
5. Score every lead as **HIGH / MEDIUM / LOW**.
6. Store leads in a real local database.
7. Export/import leads through Excel.
8. Generate personalized outreach messages.
9. Send outreach through email.
10. Support WhatsApp/SMS architecture where technically possible.
11. Track outreach status and replies.
12. Provide a professional dashboard.
13. Keep the architecture modular so paid services can be added later.

The system should be designed as a **reusable Nexomate template**, where a new client can be configured without rewriting the application.

---

# 1. IMPORTANT MVP SCOPE

For this MVP, focus on:

### CORE

- Lead sourcing
- Business/website research
- ICP generation
- Prospect discovery
- Lead scoring
- Lead database
- Excel import/export
- AI message generation
- Email outreach
- Outreach tracking
- Reply tracking
- Dashboard

### SECONDARY

- WhatsApp
- SMS

### NOT REQUIRED FOR MVP

Do not build:

- CRM integrations
- HubSpot
- GoHighLevel
- Pipedrive
- Voice AI
- Calendly/SavvyCal
- Complex appointment automation
- Enterprise multi-tenancy
- Paid email providers
- n8n

---

# 2. TECH STACK

Use a completely local/self-hosted stack.

## Backend

**Python 3.11+**

## Frontend

**Streamlit**

Create a polished SaaS-style interface rather than a default-looking Streamlit application.

## Database

**SQLite**

The database is the source of truth for application data.

## Excel

Use:

- pandas
- openpyxl

Excel is an import/export and reporting layer, NOT the primary database.

## AI

Primary:

**Ollama + locally installed LLM**

The application must work without OpenAI API access.

Create an AI abstraction layer:

```text
AIProvider
 ├── OllamaProvider
 ├── OpenAIProvider [future]
 └── OtherProvider [future]
```

This allows OpenAI to be added later without rewriting the application.

## Web research

Use free/local methods wherever possible:

- requests
- BeautifulSoup
- urllib
- DuckDuckGo/search-compatible sources
- manually imported CSV/Excel leads

Do not pretend that an unrestricted free Google/Apollo/LinkedIn API exists.

If automated discovery cannot reliably obtain a piece of information, mark it as:

```text
Not Found
```

rather than inventing data.

## Email

Use Python SMTP:

```text
smtplib
imaplib
email
```

Support Gmail/Outlook SMTP configuration.

Credentials must NOT be hardcoded.

Use environment variables or an encrypted/local configuration mechanism.

## WhatsApp

Design the system with a WhatsApp adapter.

For MVP:

- Generate WhatsApp messages.
- Store them.
- Provide a "Send via WhatsApp" action.
- If browser automation is implemented, clearly isolate it inside `whatsapp_sender.py`.

Do not claim unofficial WhatsApp automation is equivalent to the official WhatsApp Business API.

## SMS

Create an SMS adapter but don't make the entire application dependent on SMS.

If no free provider is configured:

```text
SMS status = Manual
```

and provide the generated message for copying.

---

# 3. PROJECT ARCHITECTURE

Create this structure:

```text
nexomate/
│
├── app.py
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── setup.py
│
├── database/
│   ├── database.py
│   ├── models.py
│   └── migrations.py
│
├── ai/
│   ├── base.py
│   ├── ollama_provider.py
│   ├── prompts.py
│   └── parser.py
│
├── sourcing/
│   ├── website_analyzer.py
│   ├── search_engine.py
│   ├── competitor_finder.py
│   ├── prospect_finder.py
│   ├── email_finder.py
│   └── deduplicator.py
│
├── scoring/
│   └── lead_scorer.py
│
├── outreach/
│   ├── message_generator.py
│   ├── email_sender.py
│   ├── email_tracker.py
│   ├── reply_tracker.py
│   ├── whatsapp_sender.py
│   └── sms_sender.py
│
├── excel/
│   ├── importer.py
│   ├── exporter.py
│   └── formatter.py
│
├── dashboard/
│   ├── overview.py
│   ├── leads.py
│   ├── campaigns.py
│   ├── inbox.py
│   ├── sourcing.py
│   └── settings.py
│
├── data/
│   ├── nexomate.db
│   ├── exports/
│   └── imports/
│
└── logs/
```

---

# 4. CLIENT ONBOARDING

Create a client setup screen.

Fields:

```text
Company Name
Website
Industry
Country
Target Country
Target Cities
Target Geography
Services
Ideal Customer Description
Company Size
Target Job Titles
Pain Points
Value Proposition
Preferred Tone
Sender Name
Sender Email
```

Tone options:

```text
Professional
Friendly
Direct
Casual
```

The system should also have:

### "Analyze Business"

button.

When clicked:

```text
Website
   ↓
Website Scraper
   ↓
Business Analysis
   ↓
Services
   ↓
Target Market
   ↓
ICP
   ↓
Pain Points
   ↓
Value Proposition
```

The AI should present the results to the user for approval/editing.

Do NOT automatically assume the AI's ICP is correct.

---

# 5. BUSINESS ANALYSIS

Extract:

```text
Business name
Industry
Services
Products
Locations
Service areas
Target customers
Customer problems
Value propositions
Pricing signals
Differentiators
Competitors
Relevant keywords
```

Show the result as an editable profile.

Example:

```text
YOUR BUSINESS

Solar Installation Company

Services
✓ Residential Solar
✓ Commercial Solar
✓ Battery Storage

Service Area
Texas

Target Customers
Homeowners
Property Managers
Commercial Property Owners
```

---

# 6. ICP BUILDER

Allow the user to either:

### OPTION A

Enter their ICP manually.

OR

### OPTION B

Click:

**Generate ICP with AI**

The AI generates:

```text
Target customer
Company type
Job titles
Industry
Location
Company size
Potential buying signals
Pain points
Search keywords
Exclusion criteria
```

Example:

```text
ICP:

Commercial property managers
Location: Texas
Company size: 10–500 employees

Buying signals:
- New commercial property
- High electricity costs
- Property expansion
- Sustainability initiatives
- Solar-related searches
```

---

# 7. LEAD SOURCING ENGINE

This is one of the most important parts of the product.

The sourcing pipeline:

```text
Client
 ↓
Business Analysis
 ↓
ICP
 ↓
Search Strategy
 ↓
Prospect Discovery
 ↓
Data Extraction
 ↓
Email/Phone Discovery
 ↓
Deduplication
 ↓
Lead Scoring
 ↓
Database
 ↓
Excel
```

---

# 8. PROSPECT DISCOVERY

The system must support multiple sources.

## Source 1 — Web Search

Search using generated queries based on:

```text
industry
location
job title
company type
buying signals
keywords
```

Example:

```text
commercial property managers Texas

property management companies Houston

commercial real estate managers Dallas solar

facility managers Texas
```

## Source 2 — Website Discovery

When a company website is discovered:

Extract:

```text
Company
Website
Location
Phone
Public email
Contact page
About information
Relevant employees/contact names if publicly available
```

## Source 3 — Manual Excel Import

User can upload:

```text
.xlsx
.csv
```

and import leads.

## Source 4 — Manual Entry

Allow adding individual leads.

---

# 9. NEVER INVENT LEAD DATA

This is extremely important.

If the system cannot verify:

```text
Name
Email
Phone
Company
Role
```

do NOT generate fake information.

For example:

BAD:

```text
john@company.com
```

if it wasn't actually found.

Instead:

```text
Email: Not Found
```

Every lead should have a source field:

```text
Source
Source URL
Source Type
Discovery Date
```

---

# 10. LEAD DATA MODEL

Each lead should contain:

```text
lead_id
client_id

first_name
last_name
full_name

job_title
company
website

email
phone

country
state
city

industry
company_size

source
source_url

fit_score
score_level
score_reason

buying_signals
pain_points
notes

email_status
whatsapp_status
sms_status

lead_status

created_at
updated_at
```

Lead status:

```text
NEW
REVIEWED
SELECTED
CONTACTED
REPLIED
INTERESTED
NOT_INTERESTED
FOLLOW_UP
CONVERTED
LOST
```

---

# 11. LEAD SCORING

Use a transparent scoring system.

### HIGH

```text
75–100
```

### MEDIUM

```text
50–74
```

### LOW

```text
0–49
```

Score based on configurable criteria such as:

```text
ICP match
Location match
Industry match
Job title match
Company size
Buying signals
Pain point match
Service relevance
Data quality
```

Example:

```text
Score: 91
Level: HIGH

Reason:
Commercial property manager in the client's
service area with strong relevance to the
client's solar installation offering and a
recent property expansion signal.
```

Make scoring rules editable.

---

# 12. LEADS DASHBOARD

Create a polished table.

Columns:

```text
☑
Score
Name
Company
Title
Location
Email
Phone
Source
Status
```

Example:

```text
🟢 91  Sarah Wilson
       Property Manager
       ABC Properties
       Houston, TX
       sarah@abcproperties.com
```

Color coding:

```text
HIGH    → green
MEDIUM  → yellow
LOW     → red
```

Do not rely solely on emojis; use proper visual badges.

---

# 13. LEAD FILTERS

Filters:

```text
Score
HIGH
MEDIUM
LOW

Location

Industry

Company

Status

Has Email
Has Phone

Source
```

Search:

```text
Name
Company
Email
Phone
```

Sorting:

```text
Highest score
Lowest score
Newest
Oldest
Company
```

---

# 14. EXCEL SYSTEM

Excel is extremely important.

The application must support:

### Import

```text
Import XLSX
Import CSV
```

### Export

```text
Export All Leads
Export HIGH Leads
Export MEDIUM Leads
Export LOW Leads
Export Selected Leads
```

---

# 15. EXCEL OUTPUT

Generate:

```text
Nexomate_Leads.xlsx
```

Sheets:

```text
All Leads
HIGH Priority
MEDIUM Priority
LOW Priority
Summary
```

Columns:

```text
ID
Name
Title
Company
Email
Phone
Location
Industry
Source
Source URL
Fit Score
Score Level
Score Reason
Status
Notes
Created At
```

Add:

- filters
- frozen headers
- readable column widths
- score formatting
- summary counts
- average scores

---

# 16. AI MESSAGE GENERATOR

For every selected lead, generate a personalized email.

The AI should use:

```text
Client business
Client value proposition
Lead name
Lead company
Lead role
Lead location
Relevant business information
Pain point
Reason for contacting them
```

Do NOT create generic:

> Hi, we offer amazing services...

emails.

The message should demonstrate why this particular prospect was selected.

---

# 17. EMAIL STRUCTURE

Generate:

### Subject

Short and natural.

### Opening

Personalized observation.

### Problem

Relevant problem.

### Value proposition

Explain how the client's business can help.

### CTA

Low-pressure CTA.

Example structure:

```text
Subject:
Quick question about [Company]

Hi Sarah,

I noticed that [specific observation].

Companies managing properties like yours often
run into [relevant problem].

[Client company] helps [type of customer]
with [specific value proposition].

Would it be worth a quick conversation to see
if this could make sense for [Company]?

Best,
[Sender]
```

---

# 18. MESSAGE QUALITY RULES

Every generated email must:

- be unique
- avoid fake claims
- avoid fake statistics
- avoid pretending to know something unknown
- avoid excessive personalization
- avoid spammy language
- avoid unnecessary buzzwords
- be concise
- contain a clear reason for contacting the prospect
- use the selected tone

Add:

**Regenerate**

and

**Edit**

buttons.

---

# 19. EMAIL COMPOSER

Create:

```text
Lead Information
        ↓
AI Generated Email
        ↓
Edit
        ↓
Preview
        ↓
Send / Schedule
```

UI:

```text
To:
Sarah Wilson <sarah@company.com>

Subject:
Quick question about ABC Properties

--------------------------------

Hi Sarah,

...

Best,
Farhan

--------------------------------

[Regenerate]
[Save Draft]
[Send Email]
```

---

# 20. EMAIL SENDING

Use SMTP.

Configuration:

```text
SMTP Host
SMTP Port
Sender Email
Sender Name
App Password
```

Support:

```text
Gmail
Outlook
Custom SMTP
```

Never store plaintext passwords in Excel.

Never commit credentials to Git.

---

# 21. EMAIL STATUS

Track:

```text
DRAFT
SCHEDULED
SENDING
SENT
DELIVERED
OPENED
CLICKED
REPLIED
BOUNCED
FAILED
```

If the selected SMTP provider cannot reliably provide open/click tracking, do not fake those statistics.

Show:

```text
Not available
```

instead.

---

# 22. REPLY TRACKING

Use IMAP where supported.

Periodically check the inbox.

Match incoming email against:

```text
sender email
message ID
thread
subject
lead email
```

Then update:

```text
Lead status = REPLIED
```

Store:

```text
reply_id
lead_id
message_id
sender
subject
body
received_at
```

---

# 23. REPLY CLASSIFICATION

Use AI to optionally classify replies:

```text
INTERESTED
NOT_INTERESTED
QUESTION
FOLLOW_UP
OUT_OF_OFFICE
UNKNOWN
```

Example:

```text
Sarah Wilson

"Yes, I'd be interested in learning more."

AI classification:

INTERESTED

Confidence: 94%
```

But the user must be able to override the classification.

---

# 24. UNIFIED INBOX

Create:

```text
Inbox
```

Even if email is the primary working channel, design the inbox so future channels can plug into it.

Example:

```text
─────────────────────────────────────
Sarah Wilson
ABC Properties

📧 Email

"Yes, I'd be interested in learning more."

[Interested] [Follow Up] [Archive]
─────────────────────────────────────
```

---

# 25. WHATSAPP

Implement WhatsApp as a separate adapter.

Message generation:

```text
2–3 short sentences
Conversational
Personalized
No huge paragraphs
```

Store:

```text
whatsapp_number
message
status
timestamp
```

If automated sending is unavailable, provide:

```text
Copy Message
Open WhatsApp
```

rather than pretending that a message was sent.

---

# 26. SMS

Generate short SMS:

```text
1–2 sentences
Name
Value proposition
Simple CTA
```

If no configured SMS provider exists:

```text
Copy SMS
```

instead of failing the application.

---

# 27. CAMPAIGNS

Allow users to create campaigns.

Example:

```text
Campaign:
Texas Property Managers

Industry:
Commercial Property Management

Location:
Texas

Lead count:
250
```

Campaign states:

```text
DRAFT
READY
RUNNING
PAUSED
COMPLETED
```

Campaign metrics:

```text
Total Leads
Selected
Emails Sent
Replies
Interested
Not Interested
Failed
```

---

# 28. CAMPAIGN DASHBOARD

Create KPI cards:

```text
TOTAL LEADS       1,248

HIGH PRIORITY       184

EMAILS SENT         320

REPLIES              27

INTERESTED           11
```

Charts:

```text
Lead score distribution
Outreach status
Replies over time
Leads by location
Leads by source
Campaign performance
```

---

# 29. MAIN APPLICATION NAVIGATION

Use a professional SaaS dashboard.

Sidebar:

```text
NEXOMATE

▣ Overview
◎ Find Leads
◉ Leads
✉ Outreach
↩ Inbox
▤ Campaigns
📊 Analytics
📁 Excel
⚙ Settings
```

---

# 30. DESIGN

Use the visual quality of the supplied Explee reference as inspiration, but make it **Nexomate's own product UI**.

Use:

```text
Background: #F8F9FA / white
Primary: #111111
Secondary: #6B7280
Cards: white
Borders: #E5E7EB
```

Use:

- modern typography
- rounded cards
- subtle shadows
- clean tables
- responsive layout
- professional SaaS dashboard
- minimal animations

Do NOT make it look like a generic Streamlit app.

---

# 31. OVERVIEW PAGE

Hero:

```text
Good afternoon.

Turn prospects into conversations.

Find qualified prospects, personalize
outreach, and manage your campaigns
from one workspace.
```

KPI cards:

```text
Total Leads
High Priority
Messages Sent
Replies
Interested
```

Then:

```text
Recent Leads
Recent Replies
Active Campaigns
```

---

# 32. FIND LEADS PAGE

Main workflow:

```text
STEP 1
Define Target

Industry
Location
ICP
Job Titles
Company Size

        ↓

STEP 2
Find Prospects

[Start Lead Search]

        ↓

STEP 3
Review

[View Leads]

        ↓

STEP 4
Score

AI Score Leads

        ↓

STEP 5
Save

Save to Database
Export Excel
```

Show progress during sourcing.

---

# 33. DATABASE

Use SQLite.

Tables:

```text
clients
leads
campaigns
messages
replies
business_profiles
icp_profiles
sources
```

Relationships:

```text
Client
 ├── Business Profile
 ├── ICP
 ├── Leads
 │    ├── Messages
 │    └── Replies
 └── Campaigns
```

Use migrations so database schema can evolve.

---

# 34. DATA SAFETY

Implement:

- parameterized SQL
- validation
- duplicate detection
- error handling
- logging
- database backup
- no credentials in source code
- `.env` support
- `.gitignore`
- safe file handling

Duplicate leads should be detected using combinations such as:

```text
email
phone
company + name
company + email
```

---

# 35. DUPLICATE PREVENTION

If a lead already exists:

```text
Lead already exists
```

Do not create another record.

Allow:

```text
Update existing
Skip
Review
```

---

# 36. SOURCE TRANSPARENCY

Every lead must show:

```text
Found via:
Google/Web Search

Source URL:
example.com/contact

Found:
[date]
```

This is important for trust and debugging.

---

# 37. ERROR HANDLING

The application must never crash because:

- website is unavailable
- email is missing
- phone is missing
- AI is unavailable
- search returns nothing
- malformed Excel file uploaded
- duplicate lead found
- SMTP authentication fails
- Ollama is offline

Instead show useful errors.

Example:

```text
⚠ AI service unavailable.

Ollama is not running.

Start Ollama and try again.
```

---

# 38. OFFLINE / MANUAL FALLBACK

Every major automated feature should have a manual fallback.

For example:

```text
Automatic Lead Search
        OR
Import Excel
```

and:

```text
AI Email
        OR
Manual Email
```

This makes the MVP genuinely usable.

---

# 39. SETUP

Create:

```text
README.md
setup.bat
setup.sh
requirements.txt
.env.example
```

Because the target environment may be Windows, **setup.bat is mandatory**.

Setup should:

```text
1. Install Python
2. Install dependencies
3. Install Ollama
4. Pull selected model
5. Initialize SQLite
6. Start Streamlit
```

Running:

```text
setup.bat
```

should make setup as easy as possible.

---

# 40. DEMO DATA

Include a demo mode.

Create sample:

```text
20 leads
3 campaigns
10 messages
5 replies
```

Clearly mark them:

```text
DEMO DATA
```

Do not mix fake demo leads with real leads.

---

# 41. AI PROMPT SYSTEM

Do NOT hardcode all AI prompts inside UI files.

Store prompts centrally:

```text
ai/prompts.py
```

Prompts required:

```text
business_analysis_prompt
icp_generation_prompt
competitor_analysis_prompt
lead_scoring_prompt
email_generation_prompt
reply_classification_prompt
```

AI responses must be structured JSON whenever possible.

Example:

```json
{
  "score": 87,
  "level": "HIGH",
  "reason": "Strong ICP and location match",
  "buying_signals": [
    "Recent expansion"
  ]
}
```

Validate the JSON before storing it.

---

# 42. CRITICAL RULE — NO FAKE FUNCTIONALITY

Do not create buttons that only display:

```text
Success!
```

If a button says:

```text
Find Leads
```

it must actually execute lead discovery.

If:

```text
Send Email
```

it must actually attempt SMTP sending.

If:

```text
Export Excel
```

it must actually generate an `.xlsx`.

If something cannot currently work because an external dependency isn't configured, clearly show:

```text
Not configured
```

with setup instructions.

---

# 43. DEVELOPMENT ORDER

Build in this order.

### PHASE 1

```text
Project structure
SQLite
Client setup
Dashboard
Excel import/export
```

### PHASE 2

```text
Website analyzer
ICP generator
Lead model
Lead scoring
Lead dashboard
```

### PHASE 3

```text
Web lead discovery
Deduplication
Lead source tracking
```

### PHASE 4

```text
AI email generator
Email editor
SMTP sender
Email logs
```

### PHASE 5

```text
IMAP reply tracking
Inbox
Reply classification
```

### PHASE 6

```text
WhatsApp adapter
SMS adapter
Campaigns
Analytics
```

This prevents trying to build the entire Nexomate platform simultaneously.

---

# 44. FUTURE UPGRADE ARCHITECTURE

Keep interfaces ready for:

```text
Ollama
   ↓
OpenAI

SMTP
   ↓
SendGrid / Amazon SES

SQLite
   ↓
PostgreSQL

Local search
   ↓
Paid lead providers

WhatsApp automation
   ↓
Official WhatsApp Business API

Python scheduler
   ↓
n8n / cloud workers
```

---

# 45. FINAL ACCEPTANCE TEST

The project is NOT complete until this works end-to-end:

```text
Create Client
      ↓
Enter Website
      ↓
Analyze Business
      ↓
Generate ICP
      ↓
Find Prospects
      ↓
Extract Real Information
      ↓
Score Leads
      ↓
Save to SQLite
      ↓
View in Dashboard
      ↓
Export to Excel
      ↓
Select HIGH Leads
      ↓
Generate Personalized Emails
      ↓
Edit Emails
      ↓
Send Through SMTP
      ↓
Record Send Status
      ↓
Receive Reply
      ↓
Match Reply to Lead
      ↓
Show Reply in Inbox
      ↓
Update Lead Status
      ↓
Show Campaign Statistics
```

---

# FINAL PRODUCT PRINCIPLE

The Nexomate MVP should be centered around:

**Research → Find → Verify → Score → Store → Personalize → Send → Track → Learn**

The system should prioritize verified, useful prospect information over large quantities of unreliable/fabricated leads.

Do **not** make assumptions such as "this homeowner has a high electricity bill" unless the information is actually available from a reliable source.

The goal is a practical, working MVP that can run locally with minimal/no recurring infrastructure cost and can later be upgraded to paid APIs and cloud services without redesigning the core architecture.

---

# BUILD INSTRUCTIONS TO THE CODING AGENT

Do not generate the entire project as one giant code block.

Build the application incrementally.

For every phase:

1. Create files.
2. Implement functionality.
3. Run/test it.
4. Fix errors.
5. Continue to the next phase.

At the end of each phase, verify that the existing functionality still works.

**Do not move to the next phase with broken functionality.**
