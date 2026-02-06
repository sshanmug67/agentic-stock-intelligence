"""
Analyze Stock Intent with Celery task
"""
import asyncio
from datetime import datetime
from typing import Dict, Any
from ...celery_app import celery_app  # ← Import celery_app
from ..execution.tracker import execution_tracker
from ...models.intent import IntentType


class AnalyzeStockIntent:
    """Analyze a single stock"""
    
    def __init__(self, execution_tracker):
        self.execution_tracker = execution_tracker
        self.agents = ["technical_agent", "fundamental_agent", "news_agent", "aggregation_agent"]
    
    async def execute(self, execution_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the analyze stock intent"""
        symbol = parameters.get("symbol", "UNKNOWN")
        
        print(f"🚀 Starting analysis for {symbol}")
        
        results = {}
        
        # Execute agents sequentially
        for agent_name in self.agents:
            print(f"   ⏳ Running {agent_name}...")
            self.execution_tracker.start_agent(execution_id, agent_name)
            
            # Simulate agent work
            await asyncio.sleep(1)
            
            # Generate mock result
            if agent_name == "technical_agent":
                result = {"rsi": 65.5, "macd": "bullish", "trend": "uptrend", "score": 7.5}
            elif agent_name == "fundamental_agent":
                result = {"pe_ratio": 28.5, "revenue_growth": 15.2, "profit_margin": 25.8, "score": 8.0}
            elif agent_name == "news_agent":
                result = {"sentiment": "positive", "sentiment_score": 0.75, "recent_news_count": 12}
            else:  # aggregation_agent
                result = {"recommendation": "BUY", "confidence": 0.82, "overall_score": 7.75}
            
            self.execution_tracker.complete_agent(execution_id, agent_name, True, result)
            results[agent_name.replace("_agent", "")] = result
            print(f"   ✅ {agent_name} completed")
        
        print(f"✅ Analysis complete for {symbol}")
        
        return {
            "symbol": symbol,
            "analyzed_at": datetime.utcnow().isoformat(),
            "recommendation": results["aggregation"]["recommendation"],
            "overall_score": results["aggregation"]["overall_score"],
            "confidence": results["aggregation"]["confidence"],
            "technical": results["technical"],
            "fundamental": results["fundamental"],
            "news_sentiment": results["news"]
        }


# ============================================
# Celery Task (NEW - added to this file!)
# ============================================

@celery_app.task(bind=True, name="analyze_stock")
def analyze_stock_task(self, execution_id: str, parameters: Dict[str, Any]):
    """
    Celery task for analyzing a stock
    
    This task lives with the intent it executes!
    """
    print(f"🔧 Celery Worker Processing: {execution_id}")
    print(f"   Intent: analyze_stock")
    print(f"   Parameters: {parameters}")
    
    try:
        # Create intent handler
        intent = AnalyzeStockIntent(execution_tracker)
        
        # Execute
        result = asyncio.run(intent.execute(execution_id, parameters))
        
        # Mark as complete
        execution_tracker.complete_execution(execution_id, True, result)
        
        print(f"✅ Celery Worker Completed: {execution_id}")
        return result
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Celery Worker Failed: {execution_id} - {error_msg}")
        execution_tracker.complete_execution(execution_id, False, error=error_msg)
        raise