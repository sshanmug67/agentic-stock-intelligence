"""
Base Agent - Abstract base class for all agents in the system
All agents inherit from this to get consistent:
- Error handling with retries
- Logging
- Execution timing
- Result formatting
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import time
import traceback


class BaseAgent:
    """
    Base class for all stock intelligence agents.
    
    Each agent:
    1. Has a name and description
    2. Accepts parameters (e.g., stock symbol)
    3. Runs its analysis
    4. Returns a standardized result dict
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.max_retries = 3
        self.retry_delay = 2  # seconds between retries
    
    async def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with error handling and retries.
        
        This is the method called by the intent's execute() loop.
        It wraps the actual analysis in retry logic and timing.
        
        Returns:
            {
                "agent": "agent_name",
                "status": "success" | "failed",
                "data": { ... actual results ... },
                "metadata": {
                    "executed_at": "...",
                    "duration_seconds": 1.23,
                    "retries": 0
                },
                "error": None | "error message"
            }
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"   ⏳ [{self.name}] Running (attempt {attempt}/{self.max_retries})...")
                
                # Call the actual analysis - implemented by each agent
                data = await self.execute(parameters)
                
                duration = time.time() - start_time
                print(f"   ✅ [{self.name}] Completed in {duration:.2f}s")
                
                return {
                    "agent": self.name,
                    "status": "success",
                    "data": data,
                    "metadata": {
                        "executed_at": datetime.utcnow().isoformat(),
                        "duration_seconds": round(duration, 2),
                        "retries": attempt - 1
                    },
                    "error": None
                }
                
            except Exception as e:
                last_error = str(e)
                print(f"   ⚠️ [{self.name}] Attempt {attempt} failed: {last_error}")
                
                if attempt < self.max_retries:
                    print(f"   🔄 [{self.name}] Retrying in {self.retry_delay}s...")
                    # Using synchronous sleep here since this is error recovery
                    time.sleep(self.retry_delay)
        
        # All retries exhausted
        duration = time.time() - start_time
        print(f"   ❌ [{self.name}] Failed after {self.max_retries} attempts: {last_error}")
        
        return {
            "agent": self.name,
            "status": "failed",
            "data": None,
            "metadata": {
                "executed_at": datetime.utcnow().isoformat(),
                "duration_seconds": round(duration, 2),
                "retries": self.max_retries - 1
            },
            "error": last_error
        }
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the actual analysis. Each agent implements this.
        
        Args:
            parameters: Dict containing at minimum {"symbol": "AAPL"}
        
        Returns:
            Dict with the agent's analysis results
        
        Raises:
            Exception: If analysis fails (will trigger retry in run())
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any], required_fields: list) -> None:
        """
        Validate that required parameters are present.
        Call this at the start of execute().
        
        Raises:
            ValueError: If a required field is missing
        """
        for field in required_fields:
            if field not in parameters or not parameters[field]:
                raise ValueError(f"Missing required parameter: {field}")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"