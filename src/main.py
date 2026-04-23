"""
CLI entry point for the DevOps Incident Response Agents.

Usage:
    # Single incident
    python -m src.main "Production API latency spike on /v2/orders endpoint..."

    # Automated 3-incident demo (showcases memory accumulation)
    python -m src.main --demo

    # Reset all memory banks and start fresh
    python -m src.main --reset
"""

import argparse
import sys
import time

from src.config import AGENTS_BANK_ID, DEMO_INCIDENTS, HINDSIGHT_API_URL
from src.orchestrator import run_pipeline


SEPARATOR = "=" * 80


def reset_memory_banks():
    """Delete all agent memory banks to start fresh."""
    from hindsight_client import Hindsight

    bank_suffixes = ["triage", "rca", "remediation"]

    print(f"\n{SEPARATOR}")
    print("RESETTING MEMORY BANKS")
    print(SEPARATOR)

    with Hindsight(base_url=HINDSIGHT_API_URL) as client:
        for suffix in bank_suffixes:
            bank_id = f"{AGENTS_BANK_ID}-{suffix}"
            try:
                client.delete_bank(bank_id=bank_id)
                print(f"  Deleted bank: {bank_id}")
            except Exception as e:
                print(f"  Bank {bank_id} not found or already deleted: {e}")

        # Also delete the base agents bank
        try:
            client.delete_bank(bank_id=AGENTS_BANK_ID)
            print(f"  Deleted bank: {AGENTS_BANK_ID}")
        except Exception as e:
            print(f"  Bank {AGENTS_BANK_ID} not found or already deleted: {e}")

    print("\nAll memory banks reset. Agents will start with no prior knowledge.\n")


def run_incident(incident: str, title: str = "Incident"):
    """Run the pipeline on a single incident and print results."""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)
    print(f"\nIncident Description:\n{incident}\n")
    print(f"{SEPARATOR}\n")

    results = run_pipeline(incident)

    print(f"\n{SEPARATOR}")
    print(f"  FINAL REPORT — {title}")
    print(SEPARATOR)
    for phase, output in results.items():
        print(f"\n--- {phase.upper()} ---")
        print(output)
    print(f"\n{SEPARATOR}\n")

    return results


def run_demo():
    """
    Run the full 3-incident demo to showcase memory accumulation.

    - Run 1: Agents investigate from scratch (no memory).
    - Run 2: Agents recall Run 1 findings, build on prior knowledge.
    - Run 3: Agents recognize the recurring pattern and recommend proven fixes.
    """
    print(f"\n{'#' * 80}")
    print("#  DEVOPS INCIDENT RESPONSE AGENT — MEMORY DEMO")
    print(f"#  Hindsight API: {HINDSIGHT_API_URL}")
    print(f"#  Running {len(DEMO_INCIDENTS)} sequential incidents to demonstrate")
    print("#  how agent memory improves response quality over time.")
    print(f"{'#' * 80}")

    # Start fresh for the demo
    reset_memory_banks()

    for i, incident_data in enumerate(DEMO_INCIDENTS, start=1):
        title = incident_data["title"]
        description = incident_data["description"]

        print(f"\n{'>' * 80}")
        print(f"  STARTING: {title}")
        print(f"  (Incident {i} of {len(DEMO_INCIDENTS)})")
        print(f"{'>' * 80}")

        run_incident(description, title=title)

        if i < len(DEMO_INCIDENTS):
            # Brief pause to let Hindsight consolidate observations
            wait_seconds = 5
            print(f"\nWaiting {wait_seconds}s for Hindsight to consolidate memories...")
            time.sleep(wait_seconds)

    print(f"\n{'#' * 80}")
    print("#  DEMO COMPLETE")
    print("#")
    print("#  Key takeaways:")
    print("#  - Run 1: Agents had no prior knowledge, investigated from scratch")
    print("#  - Run 2: Agents recalled Run 1 findings about DB connection pools")
    print("#  - Run 3: Agents recognized the recurring pattern and recommended")
    print("#           proven fixes (PgBouncer, connection limits) immediately")
    print("#")
    print("#  Explore the Hindsight Control Plane at http://localhost:9999")
    print("#  to see the accumulated memories, observations, and mental models.")
    print(f"{'#' * 80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="DevOps Incident Response Agent powered by Langgraph + Hindsight",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python -m src.main "API latency spike on /v2/orders..."\n'
            "  python -m src.main --demo\n"
            "  python -m src.main --reset\n"
        ),
    )
    parser.add_argument(
        "incident",
        nargs="?",
        help="Incident description text to investigate",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the full 3-incident demo showcasing memory accumulation",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset all memory banks and start fresh",
    )

    args = parser.parse_args()

    if args.reset:
        reset_memory_banks()
        if not args.incident and not args.demo:
            return

    if args.demo:
        run_demo()
    elif args.incident:
        run_incident(args.incident)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
