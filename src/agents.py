"""
Agent definitions for the DevOps Incident Response system.

Three specialized LangGraph ReAct agents, each with its own Hindsight memory
bank so expertise accumulates independently across runs.

Uses langgraph.prebuilt.create_react_agent which returns a CompiledStateGraph.
Agents are invoked with HumanMessage inputs and produce AIMessage responses.
"""

from langgraph.prebuilt import create_react_agent

from src.config import AGENTS_BANK_ID, BANK_MISSIONS
from src.hindsight_tools import make_reflect_tool, make_recall_tool, make_retain_tool
from src.llm_provider import get_llm


def _make_agent(
    role: str,
    backstory: str,
    bank_key: str,
):
    """Create a LangGraph ReAct agent with Hindsight memory tools.

    Returns a CompiledStateGraph that can be invoked with:
        result = agent.invoke({"messages": [("user", "...")]})
    """
    bank_id = f"{AGENTS_BANK_ID}-{bank_key}"

    tools = [
        make_reflect_tool(bank_id, context=BANK_MISSIONS[bank_key]),
        make_recall_tool(bank_id),
        make_retain_tool(bank_id),
    ]

    system_prompt = f"""You are {role}.

{backstory}

IMPORTANT INSTRUCTIONS:
- You MUST use your Hindsight memory tools before analyzing the incident.
- After completing your analysis, ALWAYS use hindsight_retain to store key findings.
- Be structured and thorough in your analysis."""

    llm = get_llm()

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )


def create_triage_agent():
    """Incident Triage Agent — classifies severity and detects recurring patterns."""
    return _make_agent(
        role="Incident Triage Analyst",
        backstory=(
            "You are a senior SRE with 10+ years of experience triaging production "
            "incidents. You have seen thousands of alerts and can spot patterns "
            "instantly.\n\n"
            "WORKFLOW:\n"
            "1. FIRST, use the hindsight_reflect tool to check if you have seen "
            "a similar incident before.\n"
            "2. Classify severity (P1-Critical through P4-Low).\n"
            "3. Identify affected services and blast radius.\n"
            "4. Flag if this matches a known pattern.\n"
            "5. Use hindsight_retain to store your triage findings for future reference."
        ),
        bank_key="triage",
    )


def create_rca_agent():
    """Root Cause Analysis Agent — investigates causes, recalls known failure modes."""
    return _make_agent(
        role="Root Cause Analysis Engineer",
        backstory=(
            "You are a principal infrastructure engineer who specializes in "
            "post-incident analysis. You think in dependency graphs and failure "
            "cascades.\n\n"
            "WORKFLOW:\n"
            "1. FIRST, use the hindsight_reflect tool to recall past root causes "
            "and known failure modes.\n"
            "2. Build a complete causal chain from trigger to user impact.\n"
            "3. Identify the specific component or change that triggered the incident.\n"
            "4. Assess whether this is a new failure mode or recurrence.\n"
            "5. Use hindsight_retain to store your RCA findings for future reference."
        ),
        bank_key="rca",
    )


def create_remediation_agent():
    """Remediation Agent — proposes fixes, remembers what worked before."""
    return _make_agent(
        role="Incident Remediation Specialist",
        backstory=(
            "You are a DevOps lead who has managed hundreds of incident remediations. "
            "You maintain a mental playbook of what works and what doesn't.\n\n"
            "WORKFLOW:\n"
            "1. FIRST, use the hindsight_reflect tool to check your remediation "
            "history — if a fix worked before, recommend it with confidence.\n"
            "2. Propose immediate mitigation steps (within 15 minutes).\n"
            "3. Propose short-term fixes (within 24 hours).\n"
            "4. Propose long-term preventive measures.\n"
            "5. Use hindsight_retain to store the remediation plan for future reference."
        ),
        bank_key="remediation",
    )
