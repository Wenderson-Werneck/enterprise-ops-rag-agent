"""
tests/test_agent.py
Unit tests verifying deterministic tool execution, RAG retrieval,
and response grounding.
"""

import pytest
from src.agent import EnterpriseOpsAgent
from src.tools import query_inventory_balance, calculate_freight_quote

def test_deterministic_inventory_tool():
    res = query_inventory_balance("ALLOY-FE-MN")
    assert res["found"] is True
    assert res["physical_stock_tons"] == 450.0
    assert res["available_stock_tons"] == 330.0

def test_deterministic_freight_tool():
    res = calculate_freight_quote("Terminal Alpha", "Plant North", 50.0)
    assert res["supported"] is True
    assert res["total_freight_cost_usd"] == 185.0 * 50.0

def test_agent_orchestration_flow():
    agent = EnterpriseOpsAgent()
    query = "Check available stock for Ferro-Manganese and review moisture deduction policy"
    resp = agent.handle_query(query)

    assert len(resp.tools_invoked) >= 1
    assert "ALLOY-FE-MN" in resp.tools_invoked[0]
    assert len(resp.citations) >= 1
    assert any("Discharge" in c.source_title for c in resp.citations)
    assert resp.verified_numerical_claim is True
    assert "330.0 tons" in resp.response_text or "available" in resp.response_text.lower()
