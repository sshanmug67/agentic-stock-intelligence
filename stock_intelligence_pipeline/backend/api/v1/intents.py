"""
Intent execution endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from ...models.intent import IntentRequest, IntentResponse, IntentType
from ...models.execution import ExecutionStatus
from ...graph.execution.tracker import execution_tracker
from ...graph.intents.analyze_stock import AnalyzeStockIntent

router = APIRouter()


async def execute_intent_background(execution_id: str, intent_type: str, parameters: dict):
    """Execute intent in background"""
    try:
        # Route to appropriate intent handler
        if intent_type == IntentType.ANALYZE_STOCK:
            intent = AnalyzeStockIntent(execution_tracker)
            result = await intent.execute(execution_id, parameters)
            execution_tracker.complete_execution(execution_id, True, result)
        else:
            raise ValueError(f"Intent type not implemented: {intent_type}")
            
    except Exception as e:
        print(f"❌ Execution {execution_id} failed: {str(e)}")
        execution_tracker.complete_execution(execution_id, False, error=str(e))


@router.post("/intents/execute", response_model=IntentResponse)
async def execute_intent(request: IntentRequest, background_tasks: BackgroundTasks):
    """
    Execute an intent
    
    Available intents:
    - analyze_stock: Analyze a single stock symbol
    - compare_stocks: Compare multiple stocks (coming soon)
    - market_scan: Scan market for opportunities (coming soon)
    """
    try:
        # Start execution tracking
        execution_id = execution_tracker.start_execution(
            request.intent_type.value,
            request.parameters
        )
        
        # Execute in background
        background_tasks.add_task(
            execute_intent_background,
            execution_id,
            request.intent_type.value,
            request.parameters
        )
        
        return IntentResponse(
            execution_id=execution_id,
            intent_type=request.intent_type.value,
            status=ExecutionStatus.RUNNING.value,
            message=f"Intent {request.intent_type.value} started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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