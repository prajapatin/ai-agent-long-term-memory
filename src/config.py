"""
Configuration module for the DevOps Incident Response Agents.

Loads environment variables, configures the Hindsight connection,
and defines memory bank settings for each agent.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Hindsight connection
# ---------------------------------------------------------------------------
HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")

# ---------------------------------------------------------------------------
# Memory bank definitions — one per agent for isolated expertise
# ---------------------------------------------------------------------------
AGENTS_BANK_ID = "devops-incident-agents"

BANK_MISSIONS = {
    "triage": (
        "Track production incident patterns, alert classifications, severity levels, "
        "and affected services. Recognize recurring incident signatures so that "
        "repeated issues are identified faster."
    ),
    "rca": (
        "Accumulate root cause analysis knowledge — failure modes, infrastructure "
        "correlations, dependency chains, and causal patterns. Build a knowledge base "
        "of known issues and their underlying causes."
    ),
    "remediation": (
        "Document remediation playbooks, track which fixes worked and which did not, "
        "record rollback procedures, scaling decisions, and configuration changes. "
        "Prioritize proven solutions for recurring problems."
    ),
}

# ---------------------------------------------------------------------------
# Demo incidents — used by the --demo flag to showcase memory accumulation
# ---------------------------------------------------------------------------
DEMO_INCIDENTS = [
    {
        "title": "Run 1 — Production API Latency Spike",
        "description": (
            "ALERT: Production API response times have spiked to 12s (normally 200ms). "
            "Affected service: api-gateway. The /v2/orders endpoint is timing out. "
            "CloudWatch shows CPU at 45% on app servers but database connection pool "
            "utilization is at 98%. Active DB connections jumped from 50 to 490 in the "
            "last 10 minutes. No recent deployments. RDS instance: db-prod-primary "
            "(r5.xlarge). Application logs show 'could not obtain connection from pool' "
            "errors. User-facing impact: ~30% of requests returning 504 Gateway Timeout."
        ),
    },
    {
        "title": "Run 2 — Database Connection Pool Exhausted",
        "description": (
            "ALERT: Complete database connection pool exhaustion on db-prod-primary. "
            "All 500 connections are in use. PostgreSQL pg_stat_activity shows 312 "
            "connections in 'idle in transaction' state. The payments microservice "
            "deployed version 2.4.1 three hours ago — changelog mentions a switch from "
            "synchronous to async DB queries. Connection leak suspected. api-gateway "
            "is now returning 503 on all endpoints. Queue depth on SQS order-processing "
            "is growing: 15,000 messages backlogged."
        ),
    },
    {
        "title": "Run 3 — Recurring Latency Spike After New Deployment",
        "description": (
            "ALERT: API latency spike detected again — pattern matches previous incidents. "
            "Response times at 8s on the /v2/orders endpoint. Database connection pool at "
            "92% utilization. This started 20 minutes after deploying inventory-service "
            "v3.1.0. The deployment included a new batch-sync feature that opens dedicated "
            "DB connections. No connection pooler (PgBouncer) in place yet despite being "
            "recommended in prior incident reviews. Team is asking: should we rollback "
            "or apply connection limits?"
        ),
    },
]
