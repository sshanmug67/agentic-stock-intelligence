from typing import TypedDict, Annotated, Optional
from datetime import datetime
from langgraph.graph import add_messages

class BaseGraphState(TypedDict):
    """Base state for all intent graphs"""
    
    # Execution metadata
    execution_id: str
    intent_type: str
    status: str
    started_at: datetime
    
    # Input parameters
    parameters: dict
    
    # Messages (for LangGraph)
    messages: Annotated[list, add_messages]
    
    # Agent results
    agent_results: dict  # {agent_name: result}
    
    # Errors
    errors: list
    retry_count: int
    
    # Final output
    final_result: Optional[dict]