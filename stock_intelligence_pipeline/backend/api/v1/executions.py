"""
Execution status endpoints
"""
from fastapi import APIRouter, HTTPException
from ...models.execution import ExecutionRecord
from ...graph.execution.tracker import execution_tracker

router = APIRouter()


@router.get("/executions/{execution_id}", response_model=ExecutionRecord)
async def get_execution(execution_id: str):
    """Get execution status by ID"""
    execution = execution_tracker.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return execution


@router.get("/executions", response_model=list[ExecutionRecord])
async def list_executions(limit: int = 50):
    """List recent executions"""
    return execution_tracker.list_executions(limit=limit)


@router.get("/executions/{execution_id}/agents")
async def get_execution_agents(execution_id: str):
    """Get agent execution details"""
    execution = execution_tracker.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    return {
        "execution_id": execution_id,
        "agents": execution.agents
    }