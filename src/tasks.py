"""
Task prompt templates for each agent in the DevOps Incident Response pipeline.

Each function returns a formatted string that serves as the agent's input,
incorporating the incident description and previous agent outputs.
"""


def triage_prompt(incident: str) -> str:
    """Build the triage agent's input prompt."""
    return (
        f"A new production incident has been reported. Analyze it and produce "
        f"a triage assessment.\n\n"
        f"**Incident Report:**\n{incident}\n\n"
        f"**Your job:**\n"
        f"1. FIRST, use the hindsight_reflect tool to query: "
        f"'Have we seen similar incidents involving these symptoms before?'\n"
        f"2. Classify the severity level (P1-Critical through P4-Low)\n"
        f"3. Identify all affected services and the blast radius\n"
        f"4. Flag if this matches a previously known incident pattern\n"
        f"5. Provide an initial hypothesis for the cause\n"
        f"6. Use hindsight_retain to store your key triage findings\n\n"
        f"Produce a structured triage report with: severity, affected services, "
        f"known pattern match, initial hypothesis, and investigation priority."
    )


def rca_prompt(incident: str, triage_output: str) -> str:
    """Build the RCA agent's input prompt, including triage results."""
    return (
        f"Perform a deep root cause analysis for the following incident.\n\n"
        f"**Incident Report:**\n{incident}\n\n"
        f"**Triage Assessment (from prior agent):**\n{triage_output}\n\n"
        f"**Your job:**\n"
        f"1. FIRST, use the hindsight_reflect tool to query: "
        f"'What are known root causes for database connection pool issues "
        f"and API latency spikes?'\n"
        f"2. Build a complete causal chain from trigger to user impact\n"
        f"3. Identify the specific component or change that triggered the incident\n"
        f"4. Assess whether this is a new failure mode or a recurrence\n"
        f"5. Document contributing factors (capacity, config, code changes)\n"
        f"6. Use hindsight_retain to store your RCA findings\n\n"
        f"Produce a detailed RCA report with: root cause, causal chain, "
        f"new vs recurrence assessment, contributing factors, and past comparisons."
    )


def remediation_prompt(incident: str, triage_output: str, rca_output: str) -> str:
    """Build the remediation agent's input prompt, including prior outputs."""
    return (
        f"Propose a remediation plan based on the incident analysis below.\n\n"
        f"**Incident Report:**\n{incident}\n\n"
        f"**Triage Assessment:**\n{triage_output}\n\n"
        f"**Root Cause Analysis:**\n{rca_output}\n\n"
        f"**Your job:**\n"
        f"1. FIRST, use the hindsight_reflect tool to query: "
        f"'What remediation steps have worked for database connection pool "
        f"exhaustion and API latency incidents? What should we avoid?'\n"
        f"2. Propose immediate mitigation steps (within 15 minutes)\n"
        f"3. Propose short-term fixes (within 24 hours)\n"
        f"4. Propose long-term preventive measures\n"
        f"5. Define rollback criteria and estimated recovery time\n"
        f"6. If a fix worked before, explicitly recommend it\n"
        f"7. If a fix failed before, warn against it\n"
        f"8. Use hindsight_retain to store the remediation plan\n\n"
        f"Produce a structured remediation plan with: immediate steps, short-term "
        f"fixes, long-term measures, rollback criteria, ETR, and action items."
    )
