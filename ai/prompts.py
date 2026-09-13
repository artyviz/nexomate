# ai/prompts.py
"""Centralized prompt templates for all AI operations in Nexomate."""


BUSINESS_ANALYSIS_PROMPT = """Analyze the following website content and extract structured business information.

Website URL: {url}
Website Content:
{content}

Return a JSON object with these fields:
{{
  "business_name": "...",
  "industry": "...",
  "services": ["service1", "service2"],
  "products": ["product1", "product2"],
  "locations": ["location1"],
  "service_areas": ["area1", "area2"],
  "target_customers": ["customer_type1", "customer_type2"],
  "customer_problems": ["problem1", "problem2"],
  "value_propositions": ["vp1", "vp2"],
  "pricing_signals": ["signal1"],
  "differentiators": ["diff1"],
  "competitors": ["competitor1"],
  "keywords": ["keyword1", "keyword2"]
}}

Only include information that is clearly present or strongly implied by the website content.
Do NOT invent or guess information that isn't supported by the content.
Return ONLY the JSON object, no additional text."""


ICP_GENERATION_PROMPT = """Based on the following business profile, generate an Ideal Customer Profile (ICP).

Business: {business_name}
Industry: {industry}
Services: {services}
Location: {location}
Target Customers: {target_customers}
Pain Points: {pain_points}
Value Proposition: {value_proposition}

Return a JSON object:
{{
  "target_customer": "description of ideal customer",
  "company_type": "type of company to target",
  "job_titles": ["title1", "title2", "title3"],
  "industry": "target industry",
  "location": "target geography",
  "company_size": "e.g. 10-500 employees",
  "buying_signals": ["signal1", "signal2", "signal3"],
  "pain_points": ["pain1", "pain2", "pain3"],
  "search_keywords": ["keyword1", "keyword2", "keyword3"],
  "exclusion_criteria": ["exclude1", "exclude2"]
}}

Be specific and actionable. Return ONLY the JSON object."""


COMPETITOR_ANALYSIS_PROMPT = """Identify potential competitors for this business based on the information provided.

Business: {business_name}
Industry: {industry}
Services: {services}
Location: {location}

Return a JSON array of competitor types and search strategies:
{{
  "competitor_types": ["type1", "type2"],
  "search_queries": ["query1", "query2", "query3"]
}}

Return ONLY the JSON object."""


LEAD_SCORING_PROMPT = """Score this lead against the Ideal Customer Profile.

ICP:
- Target Customer: {icp_target}
- Industry: {icp_industry}
- Location: {icp_location}
- Company Size: {icp_company_size}
- Job Titles: {icp_job_titles}
- Buying Signals: {icp_buying_signals}
- Pain Points: {icp_pain_points}

Lead:
- Name: {lead_name}
- Company: {lead_company}
- Title: {lead_title}
- Industry: {lead_industry}
- Location: {lead_location}
- Company Size: {lead_company_size}
- Additional Info: {lead_notes}

Score from 0-100 based on:
- ICP match (0-25)
- Location match (0-15)
- Industry match (0-15)
- Job title match (0-15)
- Company size match (0-10)
- Buying signals (0-10)
- Data quality (0-10)

Return a JSON object:
{{
  "score": 85,
  "level": "HIGH",
  "reason": "Brief explanation of the score",
  "breakdown": {{
    "icp_match": 20,
    "location_match": 15,
    "industry_match": 12,
    "job_title_match": 13,
    "company_size_match": 8,
    "buying_signals": 9,
    "data_quality": 8
  }}
}}

Return ONLY the JSON object."""


EMAIL_GENERATION_PROMPT = """Generate a personalized cold outreach email.

Sender Business:
- Company: {sender_company}
- Services: {sender_services}
- Value Proposition: {sender_value_prop}

Recipient:
- Name: {lead_name}
- Company: {lead_company}
- Role: {lead_title}
- Location: {lead_location}
- Industry: {lead_industry}
- Relevant Info: {lead_notes}
- Pain Points: {pain_points}

Tone: {tone}
Sender Name: {sender_name}

Rules:
- The email must be unique and personalized
- Do NOT make fake claims or statistics
- Do NOT pretend to know information you don't have
- Do NOT use spammy language or excessive buzzwords
- Keep it concise (under 150 words)
- Include a clear, low-pressure call to action
- The email should demonstrate WHY this particular prospect was selected

Return a JSON object:
{{
  "subject": "Short, natural subject line",
  "body": "The complete email body"
}}

Return ONLY the JSON object."""


REPLY_CLASSIFICATION_PROMPT = """Classify this email reply.

Original outreach was about: {context}

Reply from: {sender}
Subject: {subject}
Body:
{body}

Classify the reply as one of:
- INTERESTED: They want to learn more or schedule a call
- NOT_INTERESTED: They declined or asked to be removed
- QUESTION: They asked a question but didn't commit
- FOLLOW_UP: They want to continue the conversation later
- OUT_OF_OFFICE: Automated out-of-office reply
- UNKNOWN: Cannot determine intent

Return a JSON object:
{{
  "classification": "INTERESTED",
  "confidence": 0.94,
  "summary": "Brief summary of the reply intent"
}}

Return ONLY the JSON object."""


WHATSAPP_MESSAGE_PROMPT = """Generate a short WhatsApp message for cold outreach.

Sender: {sender_company}
Recipient: {lead_name} at {lead_company}
Value Proposition: {value_prop}
Tone: {tone}

Rules:
- 2-3 short sentences maximum
- Conversational and natural
- Personalized with their name and company
- No large paragraphs
- Include a simple question or CTA

Return a JSON object:
{{
  "message": "The WhatsApp message"
}}

Return ONLY the JSON object."""


SMS_MESSAGE_PROMPT = """Generate a short SMS message for outreach.

Sender: {sender_company}
Recipient: {lead_name}
Value Proposition: {value_prop}

Rules:
- 1-2 sentences maximum
- Include the recipient's name
- Brief value proposition
- Simple CTA
- Under 160 characters if possible

Return a JSON object:
{{
  "message": "The SMS message"
}}

Return ONLY the JSON object."""
