# AI Agent Long-Term Memory with Hindsight

A technical blog companion project demonstrating **persistent memory for AI agents** using [Hindsight](https://hindsight.vectorize.io/), [LangGraph](https://langchain-ai.github.io/langgraph/), and [LangChain](https://python.langchain.com/). This project leverages LangGraph to create a more robust and efficient AI agent memory system.

## The Problem

AI agents forget everything between sessions. Every conversation starts from zero — no context about previous incidents, no learned patterns, no institutional knowledge. This fundamentally limits what AI agents can do in production environments.

## The Solution

[Hindsight](https://hindsight.vectorize.io/) provides a purpose-built memory system for AI agents with:
- **retain()**: Store memories (facts, experiences, observations)
- **recall()**: Search memories using multi-strategy retrieval (TEMPR)
- **reflect()**: Generate contextual, disposition-aware responses from memory

## Demo Scenario: DevOps Incident Response

Three specialized LangGraph ReAct agents collaborate on production incidents, each with its own Hindsight memory bank:

| Agent | Role | Memory Bank |
|-------|------|-------------|
| **Incident Triage Analyst** | Classifies severity, detects recurring patterns | `devops-incident-agents-triage` |
| **Root Cause Analysis Engineer** | Investigates causes, recalls known failure modes | `devops-incident-agents-rca` |
| **Remediation Specialist** | Proposes fixes, remembers what worked before | `devops-incident-agents-remediation` |

### Memory Accumulation Across Runs

```
Run 1: "API Latency Spike"
  → Agents investigate from scratch (no memory)
  → Discover DB connection pool issues

Run 2: "DB Connection Pool Exhausted"
  → Agents RECALL Run 1 findings about DB connections
  → Build on prior knowledge, faster diagnosis

Run 3: "Recurring Latency Spike"
  → Agents RECOGNIZE the pattern immediately
  → Recommend proven fixes (PgBouncer, connection limits)
  → Skip redundant investigation
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           LangGraph Agent Pipeline                  │
│              (Sequential Orchestrator)              │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐      │
│  │ Triage   │→ │   RCA    │→ │ Remediation   │      │
│  │ Agent    │  │  Agent   │  │    Agent      │      │
│  └────┬─────┘  └────┬─────┘  └──────┬────────┘      │
│       │             │               │               │
│       │  Hindsight Tools (per agent)│               │
│       │  reflect / recall / retain  │               │
└───────┼─────────────┼───────────────┼────────────── ┘
        │             │               │
        ▼             ▼               ▼
┌─────────────────────────────────────────────────────┐
│              Hindsight Memory Server                │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐      │
│  │ triage   │  │   rca    │  │ remediation   │      │
│  │  bank    │  │  bank    │  │    bank       │      │
│  └──────────┘  └──────────┘  └───────────────┘      │
│                                                     │
│  retain() ←→ recall() ←→ reflect()                  │
│  Observation Consolidation | TEMPR Retrieval        │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker (for Hindsight server)
- Python 3.10+ (tested with 3.12)
- An API key for at least one LLM provider (OpenAI, Groq, or local Ollama)

### 1. Clone and Configure

```bash
git clone <this-repo>
cd ai-agent-long-term-memory

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Hindsight Server

```bash
docker compose up -d
```

This starts:
- **Hindsight API** at `http://localhost:8888`
- **Control Plane (Web UI)** at `http://localhost:9999`

### 3. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run the Demo

```bash
# Full 3-incident demo showcasing memory accumulation
python -m src.main --demo
```

### Other Commands

```bash
# Single incident
python -m src.main "Production API latency spike on /v2/orders endpoint..."

# Reset memory banks (start fresh)
python -m src.main --reset

# Reset + demo
python -m src.main --reset --demo
```

## LLM Provider Configuration

This project uses an **abstract LLM factory** (`src/llm_provider.py`) that returns a LangChain chat model — swap providers without touching agent code:

| Provider | Environment Variables | Model |
|----------|----------------------|-------|
| **OpenAI** | `LLM_PROVIDER=openai`, `OPENAI_API_KEY` | `ChatOpenAI` (gpt-4.1-mini) |
| **Groq** | `LLM_PROVIDER=groq`, `GROQ_API_KEY` | `ChatGroq` (llama-3.3-70b-versatile) |
| **Ollama** | `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | `ChatOllama` (llama3) |

The factory returns a `BaseChatModel` instance — all LangGraph agents use the same interface regardless of provider.

> **Note**: The Hindsight server uses its own LLM provider (configured via `HINDSIGHT_LLM_*` env vars in `.env`). This is independent of the agent LLM provider.

## Project Structure

```
├── docker-compose.yml          # Hindsight server (one-command setup)
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── src/
│   ├── llm_provider.py         # Abstract LLM factory (OpenAI/Groq/Ollama)
│   ├── config.py               # Hindsight connection + bank configuration
│   ├── hindsight_tools.py      # LangChain tools: reflect, recall, retain
│   ├── agents.py               # 3 LangGraph ReAct agents with Hindsight tools
│   ├── tasks.py                # Prompt templates for each pipeline stage
│   ├── orchestrator.py          # Sequential pipeline orchestrator
│   └── main.py                 # CLI entry point
```

## Exploring Memory in the Control Plane

After running the demo, open `http://localhost:9999` to explore:

- **Memory Banks**: See the 3 agent-specific banks and their accumulated knowledge
- **Observations**: Hindsight automatically consolidates raw facts into evidence-grounded beliefs
- **Entity Graph**: Visualize relationships between services, incidents, and fixes

## Key Hindsight Concepts Demonstrated

1. **retain()**: Agents explicitly store findings via the `hindsight_retain` tool after each analysis
2. **recall()**: Agents search raw memories via the `hindsight_recall` tool for specific facts
3. **reflect()**: Agents synthesize contextual answers via `hindsight_reflect` for disposition-aware reasoning
4. **Observation Consolidation**: Overlapping facts merge into durable observations with evidence tracking
5. **Per-Agent Banks**: Each agent builds isolated expertise (triage patterns ≠ remediation playbooks)
6. **Bank Missions**: Guide how Hindsight organizes and prioritizes knowledge

## Links

- [Hindsight Documentation](https://hindsight.vectorize.io/)
- [Hindsight GitHub](https://github.com/vectorize-io/hindsight)
- [LangChain Documentation](https://python.langchain.com/)
- [Hindsight Python Client](https://hindsight.vectorize.io/sdks/python)
