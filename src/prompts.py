EXTRACT_INFO_PROMPT = """
You are an expert sales analyst. Analyze the following sales call transcript
and extract structured information.

Transcript:
{transcript}

Extract and return a JSON object with exactly these fields:
{{
    "prospect_name": "first and last name of the prospect",
    "company_name": "prospect's company name",
    "deal_stage": "one of: Discovery, Proposal, Negotiation, Closing",
    "objections": ["list of objections raised by the prospect"],
    "commitments": ["list of things the salesperson committed to do"],
    "next_steps": ["list of agreed next steps"]
}}

Return only valid JSON. No explanation.
"""

DRAFT_EMAIL_PROMPT = """
You are writing a post-call summary email on behalf of the salesperson.

Call details:
- Prospect: {prospect_name} at {company_name}
- Deal stage: {deal_stage}
- Commitments made: {commitments}
- Next steps agreed: {next_steps}

Write a concise, professional follow-up email (under 150 words) that:
1. Thanks them for their time
2. Summarizes the key commitments
3. Confirms the next steps with a soft call to action

Return only the email body. No subject line.
"""

FLAG_RISKS_PROMPT = """
You are a sales risk analyst. Review this sales call transcript and identify risk signals.

Transcript:
{transcript}

Known objections: {objections}

Look for these specific signals:
- Competitor mentions (name the competitor)
- Budget concerns or constraints
- Missing decision maker ("I need to check with...")
- Timeline stalls ("let's revisit in Q3...")
- Lukewarm engagement signals

Return a JSON object:
{{
    "risk_flags": ["list of specific risk signals found"],
    "risk_level": "low | medium | high"
}}

Risk level guide:
- low: no significant signals
- medium: 1-2 signals, deal still healthy
- high: 3+ signals or a critical blocker present

Return only valid JSON. No explanation.
"""
