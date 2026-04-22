from typing import TypedDict


class CallDebriefState(TypedDict):
    # --- INPUT ---
    transcript: str

    # --- EXTRACTED (filled by extract_info node) ---
    deal_stage: str
    objections: list[str]
    commitments: list[str]
    next_steps: list[str]
    prospect_name: str
    company_name: str

    # --- CRM (filled by update_crm node) ---
    crm_record: dict

    # --- TASK (filled by create_task node) ---
    follow_up_task: dict

    # --- EMAIL (filled by draft_email node) ---
    summary_email: str

    # --- RISKS (filled by flag_risks node) ---
    risk_flags: list[str]
    risk_level: str  # "low" | "medium" | "high"

    # --- HUMAN REVIEW ---
    human_approved: bool
    human_edits: str

    # --- OUTPUT ---
    final_report: dict
