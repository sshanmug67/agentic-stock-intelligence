"""
Intent execution endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from ...models.intent import (
    IntentRequest, 
    IntentResponse, 
    IntentType,
)

from ...models.execution import ExecutionStatus
from ...graph.execution.tracker import execution_tracker

# Import the task from intent file (NEW!)
from ...graph.intents.analyze_stock import analyze_stock_task

router = APIRouter()

@router.post("/intents/execute", response_model=IntentResponse)
async def execute_intent(request: IntentRequest):
    """
    Execute an intent using Celery
    """
    try:
        # Create execution record
        execution_id = execution_tracker.start_execution(
            request.intent_type.value,
            request.parameters
        )
        
        print(f"📍 Intent execution requested: {execution_id}")

        # Route to appropriate task (NEW!)
        if request.intent_type == IntentType.ANALYZE_STOCK:
            task = analyze_stock_task.delay(execution_id, request.parameters)
        else:
            raise HTTPException(400, f"Intent type not implemented: {request.intent_type}")

        print(f"✅ Task sent to Celery: {task.id}")
        
        return IntentResponse(
            execution_id=execution_id,
            intent_type=request.intent_type.value,
            status=ExecutionStatus.RUNNING.value,
            message=f"Intent {request.intent_type.value} started successfully",
            celery_task_id=task.id
        )
        
    except Exception as e:
        print(f"❌ Failed to start intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/intents/types")
async def list_intent_types():
    """List available intent types"""
    return {
        "intent_types": [
            {
                "type": "analyze_stock",
                "description": "Analyze a single stock symbol",
                "parameters": {
                    "symbol": "Stock symbol (e.g., AAPL)",
                    "analysis_depth": "Optional: quick or deep (default: deep)"
                },
                "status": "active"
            },
            {
                "type": "compare_stocks",
                "description": "Compare multiple stocks",
                "parameters": {
                    "symbols": "List of stock symbols"
                },
                "status": "coming_soon"
            },
            {
                "type": "market_scan",
                "description": "Scan market for opportunities",
                "parameters": {
                    "sector": "Optional sector filter"
                },
                "status": "coming_soon"
            }
        ]
    }