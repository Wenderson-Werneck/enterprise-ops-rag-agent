"""
src/tools.py
Deterministic operational tools invoked by the AI planner.
Guarantees exact mathematical calculation without probabilistic hallucination.
"""

from typing import Dict, Any, List

# Synthetic mock database for deterministic queries
MOCK_INVENTORY_DB = {
    "ALLOY-FE-MN": {"name": "High Carbon Ferro-Manganese", "stock_tons": 450.0, "port_location": "Terminal Alpha", "reserved_tons": 120.0},
    "ALLOY-SI-MN": {"name": "Silico-Manganese Grade 65/17", "stock_tons": 820.0, "port_location": "Terminal Beta", "reserved_tons": 0.0},
    "CHEM-SODA-ASH": {"name": "Dense Soda Ash Industrial", "stock_tons": 1250.0, "port_location": "Warehouse Charlie", "reserved_tons": 300.0},
}

MOCK_FREIGHT_MATRIX = {
    ("Terminal Alpha", "Plant North"): {"distance_km": 420, "base_rate_per_ton": 185.0},
    ("Terminal Beta", "Plant South"): {"distance_km": 680, "base_rate_per_ton": 265.0},
    ("Warehouse Charlie", "Plant Central"): {"distance_km": 310, "base_rate_per_ton": 145.0},
}

def query_inventory_balance(commodity_code: str) -> Dict[str, Any]:
    """Retrieves exact physical and reserved inventory balances for an industrial commodity."""
    code = commodity_code.upper().strip()
    record = MOCK_INVENTORY_DB.get(code)
    if not record:
        return {"found": False, "error": f"Commodity code '{code}' not recognized in enterprise catalog."}
    
    available = record["stock_tons"] - record["reserved_tons"]
    return {
        "found": True,
        "commodity_code": code,
        "name": record["name"],
        "physical_stock_tons": record["stock_tons"],
        "reserved_stock_tons": record["reserved_tons"],
        "available_stock_tons": available,
        "port_location": record["port_location"]
    }

def calculate_freight_quote(origin_terminal: str, destination_plant: str, tonnage: float) -> Dict[str, Any]:
    """Calculates deterministic transport cost based on negotiated corridor rates and tonnage."""
    corridor = (origin_terminal.strip(), destination_plant.strip())
    rate_info = MOCK_FREIGHT_MATRIX.get(corridor)
    if not rate_info:
        return {"supported": False, "error": f"No active contract for corridor '{corridor[0]}' -> '{corridor[1]}'"}
    
    rate = rate_info["base_rate_per_ton"]
    total = round(rate * tonnage, 2)
    return {
        "supported": True,
        "origin": corridor[0],
        "destination": corridor[1],
        "distance_km": rate_info["distance_km"],
        "tonnage": tonnage,
        "rate_per_ton": rate,
        "total_freight_cost_usd": total
    }

OPERATIONAL_TOOL_DEFINITIONS = [
    {
        "name": "query_inventory_balance",
        "description": "Look up physical and available inventory balances for an industrial commodity.",
        "parameters": {
            "type": "object",
            "properties": {
                "commodity_code": {"type": "string", "description": "Commodity code (e.g. ALLOY-FE-MN, ALLOY-SI-MN, CHEM-SODA-ASH)"}
            },
            "required": ["commodity_code"]
        }
    },
    {
        "name": "calculate_freight_quote",
        "description": "Calculate deterministic freight costs between deepwater port terminals and manufacturing plants.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin_terminal": {"type": "string", "description": "Origin port terminal"},
                "destination_plant": {"type": "string", "description": "Destination manufacturing plant"},
                "tonnage": {"type": "number", "description": "Total metric tons to transport"}
            },
            "required": ["origin_terminal", "destination_plant", "tonnage"]
        }
    }
]
