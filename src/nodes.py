import os
from dotenv import load_dotenv
load_dotenv()

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from .state import CallDebriefState
from .prompts import EXTRACT_INFO_PROMPT, DRAFT_EMAIL_PROMPT, FLAG_RISKS_PROMPT

llm = ChatOpenAI(
    model="meta/llama-3.1-70b-instruct",
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
    temperature=0,
)


def parse_json_response(text: str) -> dict:
    """
    Clean model output and parse JSON safely.

    WHY:
    Some models wrap JSON in markdown code fences like:
    ```json
    {...}
    ```
    or
    ```
    {...}
    ```

    json.loads() cannot parse that directly, so we strip the fences first.
    """
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        # Remove first fence line
        lines = lines[1:]

        # Remove last fence line if present
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return json.loads(text)


def extract_info(state: CallDebriefState) -> dict:
    prompt = EXTRACT_INFO_PROMPT.format(transcript=state["transcript"])
    response = llm.invoke([HumanMessage(content=prompt)])
    extracted = parse_json_response(response.content)
    return {
        "prospect_name": extracted["prospect_name"],
        "company_name": extracted["company_name"],
        "deal_stage": extracted["deal_stage"],
        "objections": extracted["objections"],
        "commitments": extracted["commitments"],
        "next_steps": extracted["next_steps"],
    }


def update_crm(state: CallDebriefState) -> dict:
    crm_record = {
        "prospect": state["prospect_name"],
        "company": state["company_name"],
        "deal_stage": state["deal_stage"],
        "objections": state["objections"],
        "last_contact": "2026-04-22",
        "status": "updated",
    }
    print(f"[CRM] Record updated for {state['company_name']}")
    return {"crm_record": crm_record}


def create_task(state: CallDebriefState) -> dict:
    all_actions = state["commitments"] + state["next_steps"]
    description = " | ".join(all_actions) if all_actions else "Follow up from call"
    follow_up_task = {
        "title": f"Follow up: {state['company_name']} call",
        "description": description,
        "due_date": "2026-04-25",
        "assigned_to": "Sales Rep",
        "priority": "high" if state.get("risk_level") == "high" else "normal",
    }
    print(f"[TASK] Created follow-up task for {state['company_name']}")
    return {"follow_up_task": follow_up_task}


def draft_email(state: CallDebriefState) -> dict:
    prompt = DRAFT_EMAIL_PROMPT.format(
        prospect_name=state["prospect_name"],
        company_name=state["company_name"],
        deal_stage=state["deal_stage"],
        commitments=state["commitments"],
        next_steps=state["next_steps"],
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"summary_email": response.content}


def flag_risks(state: CallDebriefState) -> dict:
    prompt = FLAG_RISKS_PROMPT.format(
        transcript=state["transcript"],
        objections=state["objections"],
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    result = parse_json_response(response.content)

    risk_level = str(result["risk_level"]).lower().strip()
    if risk_level not in ("low", "medium", "high"):
        risk_level = "medium"

    print(f"[RISK] Level: {risk_level} | Flags: {result['risk_flags']}")
    return {
        "risk_flags": result["risk_flags"],
        "risk_level": risk_level,
    }


def human_review(state: CallDebriefState) -> dict:
    print("\n" + "=" * 60)
    print("⚠️  HUMAN REVIEW REQUIRED")
    print(f"Risk Level: {state['risk_level'].upper()}")
    print(f"Risk Flags: {state['risk_flags']}")
    print(f"\nDraft Email:\n{state['summary_email']}")
    print(f"\nFollow-up Task: {state['follow_up_task']['description']}")
    print("=" * 60)

    human_input = interrupt({
        "message": "Review the output above. Type edits or press Enter to approve.",
        "current_email": state["summary_email"],
        "risk_flags": state["risk_flags"],
    })

    approved = human_input.strip() == "" or human_input.lower() == "approve"
    return {
        "human_approved": approved,
        "human_edits": human_input if not approved else "",
    }


def auto_approve(state: CallDebriefState) -> dict:
    print(f"[AUTO] Low risk — auto-approved for {state['company_name']}")
    return {
        "human_approved": True,
        "human_edits": "",
    }


def build_report(state: CallDebriefState) -> dict:
    final_report = {
        "prospect": state["prospect_name"],
        "company": state["company_name"],
        "deal_stage": state["deal_stage"],
        "objections": state["objections"],
        "commitments": state["commitments"],
        "next_steps": state["next_steps"],
        "crm_record": state["crm_record"],
        "follow_up_task": state["follow_up_task"],
        "email_draft": state["summary_email"],
        "risk_level": state["risk_level"],
        "risk_flags": state["risk_flags"],
        "approved": state["human_approved"],
        "human_edits": state.get("human_edits", ""),
    }
    print(f"\n✅ Report complete for {state['company_name']}")
    return {"final_report": final_report}