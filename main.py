import json
from pathlib import Path
from langgraph.types import Command
from src.graph import app

graph_mermaid = app.get_graph().draw_mermaid()

def load_transcript() -> str:
    """
    WHY: Load the sample transcript from the data folder.
    In production this could be a CLI argument, an API payload,
    or a file upload. We keep it simple for the demo.
    """
    transcript_path = Path("data/sample_transcript.txt")
    return transcript_path.read_text(encoding="utf-8")


def run_agent():
    """
    WHY THIS STRUCTURE:
    We split the run into two phases:
    Phase 1 — initial run: feed transcript, run until interrupt or END
    Phase 2 — resume (only if interrupted): collect human input, continue

    The thread_id ties both phases together via the checkpointer.
    Same thread_id = same conversation = LangGraph finds the saved state.
    """

    transcript = load_transcript()

    # thread_id identifies this specific run in the checkpointer.
    # In production: use uuid.uuid4() to generate a unique ID per call.
    config = {"configurable": {"thread_id": "demo-run-001"}}

    print("\n🚀 Starting Sales Call Debrief Agent...")
    print("=" * 60)
   


    # ── PHASE 1: Initial run ──────────────────────────────────────
    # stream() runs the graph and yields events as each node completes.
    # We collect events to detect if an interrupt occurred.

    interrupted = False
    interrupt_data = None

    for event in app.stream({"transcript": transcript}, config, stream_mode="values"):

        # Check if this event contains an interrupt signal
        # WHY: LangGraph surfaces interrupts as a special key in the event dict
        if "__interrupt__" in event:
            interrupted = True
            interrupt_data = event["__interrupt__"]
            break

    # ── PHASE 2: Handle interrupt if it occurred ──────────────────
    if interrupted:
        print("\n" + "=" * 60)
        print("⚠️  AGENT PAUSED — HUMAN REVIEW REQUIRED")
        print("=" * 60)

        # Show what the interrupt surfaced
        if interrupt_data:
            for item in interrupt_data:
                value = item.value if hasattr(item, "value") else item
                if isinstance(value, dict):
                    if "current_email" in value:
                        print(f"\n📧 Draft Email:\n{value['current_email']}")
                    if "risk_flags" in value:
                        print(f"\n🚩 Risk Flags: {value['risk_flags']}")
                    if "message" in value:
                        print(f"\n💬 {value['message']}")

        print("\n" + "-" * 60)
        human_input = input("Your input (press Enter to approve, or type edits): ")

        # Resume the graph with human input
        # WHY Command(resume=...): this is LangGraph's way of injecting
        # human input back into the interrupted graph. The same thread_id
        # tells the checkpointer which paused run to resume.
        print("\n▶️  Resuming agent...")
        final_state = app.invoke(Command(resume=human_input), config)

    else:
        # No interrupt occurred — low risk, auto-approved
        # Get final state by invoking with None (graph already finished)
        final_state = app.get_state(config).values

    # ── OUTPUT ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("📋 FINAL REPORT")
    print("=" * 60)

    if final_state and "final_report" in final_state:
        report = final_state["final_report"]
        print(f"\nProspect:    {report.get('prospect')}")
        print(f"Company:     {report.get('company')}")
        print(f"Deal Stage:  {report.get('deal_stage')}")
        print(f"Risk Level:  {report.get('risk_level')}")
        print(f"\nObjections:  {report.get('objections')}")
        print(f"Commitments: {report.get('commitments')}")
        print(f"Next Steps:  {report.get('next_steps')}")
        print(f"\nRisk Flags:  {report.get('risk_flags')}")
        print(f"Approved:    {report.get('approved')}")
        if report.get('human_edits'):
            print(f"Human Edits: {report.get('human_edits')}")
        print(f"\n📧 Final Email Draft:\n{report.get('email_draft')}")

        # Save report to JSON file
        # WHY: gives you a tangible output artifact to show clients
        output_path = Path("output_report.json")
        output_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"\n💾 Report saved to {output_path}")

        graph_path = Path("graph.mmd")
        graph_path.write_text(graph_mermaid, encoding="utf-8")
        print(f"🗺️ Graph Mermaid saved to {graph_path}")
    else:
        print("No final report found in state.")


if __name__ == "__main__":
    run_agent()
