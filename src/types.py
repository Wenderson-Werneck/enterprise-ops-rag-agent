"""
src/types.py
Data contracts and state schemas for the enterprise agent architecture.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_title: str
    source_uri: str
    content: str
    section: str
    score: float = 0.0

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    data: Any
    error_message: Optional[str] = None

class GroundedCitation(BaseModel):
    source_title: str
    locator: str
    confidence: float

class AgentResponse(BaseModel):
    query: str
    response_text: str
    tools_invoked: List[str] = Field(default_factory=list)
    citations: List[GroundedCitation] = Field(default_factory=list)
    verified_numerical_claim: bool = True
    session_id: str
