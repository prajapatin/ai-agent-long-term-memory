"""
Orchestrator for the DevOps Incident Response pipeline.

Runs three LangGraph ReAct agents sequentially — triage → RCA → remediation —
passing each agent's output to the next. Each agent uses Hindsight tools
to recall/retain knowledge across runs.
"""

from src.agents import (
    create_triage_agent,
    create_rca_agent,
    create_remediation_agent,
)
from src.tasks import triage_prompt, rca_prompt, remediation_prompt


def _invoke_agent(agent, prompt: str) -> str:
    """Invoke a LangGraph ReAct agent and extract the final text response."""
    result = agent.invoke({"messages": [("user", prompt)]})
    # The result is a dict with "messages" — the last AI message is the answer
    messages = result["messages"]
    # Walk backwards to find the last AI message content
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content and not hasattr(msg, "tool_calls"):
            return msg.content
        if hasattr(msg, "content") and msg.content and hasattr(msg, "tool_calls") and not msg.tool_calls:
            return msg.content
    return str(messages[-1].content) if messages else "No response from agent."


def run_pipeline(incident: str) -> dict:
    """
    Run the full incident response pipeline.

    Sequential flow:
      1. Triage Agent → classifies severity, checks memory for patterns
      2. RCA Agent    → investigates root cause, builds on triage output
      3. Remediation  → proposes fixes, references what worked before

    Each agent has its own Hindsight memory bank:
      - devops-incident-agents-triage
      - devops-incident-agents-rca
      - devops-incident-agents-remediation

    Args:
        incident: The incident description text.

    Returns:
        Dict with keys: triage, rca, remediation (each agent's output).
    """
    results = {}

    # --- Step 1: Triage ---
    print("\n[1/3] Running Incident Triage Agent...")
    triage_agent = create_triage_agent()
    results["triage"] = _invoke_agent(triage_agent, triage_prompt(incident))
    print(f"\n--- Triage Complete ---\n{results['triage']}\n")

    # --- Step 2: Root Cause Analysis ---
    print("\n[2/3] Running Root Cause Analysis Agent...")
    rca_agent = create_rca_agent()
    results["rca"] = _invoke_agent(
        rca_agent, rca_prompt(incident, results["triage"])
    )
    print(f"\n--- RCA Complete ---\n{results['rca']}\n")

    # --- Step 3: Remediation ---
    print("\n[3/3] Running Remediation Agent...")
    remediation_agent = create_remediation_agent()
    results["remediation"] = _invoke_agent(
        remediation_agent,
        remediation_prompt(incident, results["triage"], results["rca"]),
    )
    print(f"\n--- Remediation Complete ---\n{results['remediation']}\n")

    return results
