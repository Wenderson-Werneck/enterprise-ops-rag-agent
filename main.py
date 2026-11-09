"""
main.py
CLI Demonstration and test runner for EnterpriseOpsAgent.
"""

from src.agent import EnterpriseOpsAgent

def main():
    print("=" * 70)
    print("  ENTERPRISE OPS RAG AGENT - AUTONOMOUS ORCHESTRATOR")
    print("=" * 70)

    agent = EnterpriseOpsAgent()
    sample_query = "What is the available stock for ALLOY-FE-MN at the terminal, and what is our moisture deduction policy?"

    print(f"\n[User Query]: '{sample_query}'\n")
    response = agent.handle_query(sample_query)

    print("-" * 70)
    print("  AGENT RESPONSE:")
    print("-" * 70)
    print(response.response_text)
    print("\n" + "-" * 70)
    print("  AUDIT METRICS & EXECUTION TRACE:")
    print("-" * 70)
    print(f" -> Tools Invoked:    {response.tools_invoked}")
    print(f" -> Citations Found:  {len(response.citations)}")
    for c in response.citations:
        print(f"    - {c.source_title} [{c.locator}] (Confidence: {c.confidence})")
    print(f" -> Factually Grounded: {response.verified_numerical_claim}")
    print("=" * 70)

if __name__ == "__main__":
    main()
