"""
Hindsight memory tools for LangChain agents.

Provides three LangChain tools wrapping the core Hindsight APIs:
  - hindsight_reflect: Synthesize contextual answers from memory
  - hindsight_recall:  Search raw memories by query
  - hindsight_retain:  Store new knowledge into a memory bank

Each tool is a factory function that returns a closure bound to a specific
bank_id, so agents get isolated per-bank memory access.
"""

from hindsight_client import Hindsight
from langchain_core.tools import tool

from src.config import HINDSIGHT_API_URL


def _get_client() -> Hindsight:
    """Return a Hindsight client instance."""
    return Hindsight(base_url=HINDSIGHT_API_URL)


def make_reflect_tool(bank_id: str, context: str | None = None):
    """
    Create a LangChain tool that calls Hindsight reflect() for a given bank.

    reflect() returns a synthesized, disposition-aware answer drawing on all
    relevant memories, not just raw facts.
    """

    @tool(f"hindsight_reflect_{bank_id}")
    def hindsight_reflect(query: str) -> str:
        """Query long-term memory for synthesized knowledge about past incidents,
        root causes, or remediation outcomes. Use this BEFORE investigating to
        check if similar issues have been seen before."""
        try:
            with _get_client() as client:
                response = client.reflect(
                    bank_id=bank_id,
                    query=query,
                    budget="mid",
                    context=context,
                )
                result = response.text if hasattr(response, "text") else str(response)
                if not result or result.strip() == "":
                    return (
                        "No relevant memories found. This appears to be a new type "
                        "of incident. Proceed with a fresh investigation."
                    )
                return result
        except Exception as e:
            return (
                f"Memory recall unavailable ({e}). "
                "Proceed with a fresh investigation based on the incident details."
            )

    return hindsight_reflect


def make_recall_tool(bank_id: str):
    """
    Create a LangChain tool that calls Hindsight recall() for a given bank.

    recall() returns raw memory search results using multi-strategy retrieval.
    """

    @tool(f"hindsight_recall_{bank_id}")
    def hindsight_recall(query: str) -> str:
        """Search long-term memory for raw facts, observations, and past knowledge
        related to the query. Returns individual memory entries ranked by relevance."""
        try:
            with _get_client() as client:
                response = client.recall(
                    bank_id=bank_id,
                    query=query,
                    budget="mid",
                    max_tokens=4096,
                )
                if not response.results:
                    return "No memories found for this query."
                lines = []
                for r in response.results:
                    mem_type = getattr(r, "type", "unknown")
                    lines.append(f"- [{mem_type}] {r.text}")
                return "\n".join(lines)
        except Exception as e:
            return f"Memory search unavailable ({e})."

    return hindsight_recall


def make_retain_tool(bank_id: str):
    """
    Create a LangChain tool that calls Hindsight retain() for a given bank.

    retain() stores new knowledge into the memory bank for future retrieval.
    """

    @tool(f"hindsight_retain_{bank_id}")
    def hindsight_retain(content: str) -> str:
        """Store important findings, conclusions, or lessons learned into
        long-term memory so they can be recalled in future incidents."""
        try:
            with _get_client() as client:
                client.retain(
                    bank_id=bank_id,
                    content=content,
                    context="devops incident response",
                )
                return f"Successfully stored to memory bank '{bank_id}'."
        except Exception as e:
            return f"Failed to store memory ({e})."

    return hindsight_retain
