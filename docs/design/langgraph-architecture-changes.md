# LangGraph Integration - Architecture Changes

## Overview

This document shows how the directory structure and architecture change when using LangGraph as the orchestrator for the agentic AI system.

---

## Key Architectural Changes

### Before (Traditional Orchestrator)
```
Coordinator → spawns agents in parallel → agents use tools → write to DB
```

### After (LangGraph)
```
Graph Definition → StateGraph with nodes & edges → conditional routing → checkpointing
```

### What LangGraph Provides

✅ **Stateful Execution** - Shared state flows through graph  
✅ **Conditional Routing** - Dynamic agent execution based on results  
✅ **Checkpointing** - Pause/resume analysis, recovery from failures  
✅ **Human-in-the-loop** - Add approval steps if needed  
✅ **Streaming** - Stream intermediate results  
✅ **Visualization** - Built-in graph visualization  
✅ **Error Handling** - Retry logic and fallbacks  

---

## Updated Directory Structure

### Pipeline System with LangGraph

```
stock_intelligence_pipeline/
├── backend/
│   ├── main.py
│   ├── requirements.txt  # Add langgraph, langchain
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging_config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── monitoring.py
│   │   ├── jobs.py
│   │   ├── triggers.py
│   │   └── health.py
│   │
│   ├── graph/                          # ← NEW: LangGraph definitions
│   │   ├── __init__.py
│   │   ├── state.py                    # State schemas
│   │   ├── stock_analysis_graph.py     # Main graph definition
│   │   ├── nodes/                      # Graph nodes
│   │   │   ├── __init__.py
│   │   │   ├── initialize_node.py
│   │   │   ├── technical_node.py
│   │   │   ├── fundamentals_node.py
│   │   │   ├── news_node.py
│   │   │   ├── sec_node.py
│   │   │   ├── market_context_node.py
│   │   │   ├── analyst_node.py
│   │   │   ├── aggregation_node.py
│   │   │   └── finalize_node.py
│   │   │
│   │   ├── edges/                      # Conditional edges
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── conditions.py
│   │   │
│   │   └── checkpoints/                # Checkpoint persistence
│   │       ├── __init__.py
│   │       ├── supabase_checkpointer.py
│   │       └── memory_checkpointer.py
│   │
│   ├── agents/                         # ← MODIFIED: Now used by nodes
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Simpler, used by nodes
│   │   ├── technical_agent.py
│   │   ├── fundamentals_agent.py
│   │   ├── news_sentiment_agent.py
│   │   ├── sec_filings_agent.py
│   │   ├── market_context_agent.py
│   │   ├── analyst_ratings_agent.py
│   │   ├── competitor_agent.py
│   │   └── options_agent.py
│   │
│   ├── tools/                          # Tools for LangChain/LangGraph
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── twelve_data_tool.py        # LangChain Tool wrapper
│   │   ├── alpha_vantage_tool.py
│   │   ├── finnhub_tool.py
│   │   ├── sec_edgar_tool.py
│   │   ├── news_api_tool.py
│   │   └── repository_tools.py         # DB access as tools
│   │
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── data_cleaner.py
│   │   ├── aggregator.py
│   │   ├── enricher.py
│   │   └── validator.py
│   │
│   ├── services/                       # ← NEW: Business logic services
│   │   ├── __init__.py
│   │   ├── graph_service.py           # Graph execution service
│   │   ├── checkpoint_service.py      # Checkpoint management
│   │   └── scheduler_service.py       # Scheduling with LangGraph
│   │
│   └── utils/
│       ├── __init__.py
│       ├── rate_limiter.py
│       ├── cache_manager.py
│       └── retry_helper.py
│
├── frontend/                           # Monitoring UI (mostly same)
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphVisualizer.jsx    # ← NEW: Visualize LangGraph
│   │   │   ├── CheckpointViewer.jsx   # ← NEW: View checkpoints
│   │   │   ├── AgentStatus.jsx
│   │   │   └── ...
│   │   └── ...
│   └── ...
│
├── scripts/
│   ├── run_pipeline.py
│   ├── trigger_analysis.py
│   └── visualize_graph.py             # ← NEW: Generate graph diagrams
│
└── tests/
    ├── test_graph/                     # ← NEW: Graph tests
    │   ├── test_graph_definition.py
    │   ├── test_nodes.py
    │   ├── test_edges.py
    │   └── test_checkpoints.py
    ├── test_agents/
    └── test_tools/
```

---

## Core LangGraph Components

### 1. State Schema (`graph/state.py`)

```python
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from uuid import UUID
import operator

class StockAnalysisState(TypedDict):
    """State that flows through the graph"""
    
    # Input
    ticker: str
    stock_id: UUID
    analysis_run_id: UUID
    run_type: str
    
    # Configuration
    agents_to_run: List[str]  # Which agents to execute
    max_retries: int
    
    # Agent Results
    technical_data: Optional[Dict[str, Any]]
    fundamental_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    sec_data: Optional[Dict[str, Any]]
    market_context_data: Optional[Dict[str, Any]]
    analyst_data: Optional[Dict[str, Any]]
    
    # Agent Execution Tracking
    completed_agents: Annotated[List[str], operator.add]  # Append-only list
    failed_agents: Annotated[List[str], operator.add]
    agent_errors: Dict[str, str]
    
    # Aggregated Results
    aggregated_analysis: Optional[Dict[str, Any]]
    
    # Metadata
    started_at: datetime
    completed_at: Optional[datetime]
    status: str  # 'pending', 'running', 'completed', 'failed'
    current_step: str
    
    # Checkpoint info
    checkpoint_id: Optional[str]
    can_resume: bool
```

### 2. Main Graph Definition (`graph/stock_analysis_graph.py`)

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from typing import Literal

from .state import StockAnalysisState
from .nodes import (
    initialize_node,
    technical_node,
    fundamentals_node,
    news_node,
    sec_node,
    market_context_node,
    analyst_node,
    aggregation_node,
    finalize_node,
)
from .edges.router import route_next_agent, should_continue_analysis
from .checkpoints.supabase_checkpointer import SupabaseCheckpointer


def create_stock_analysis_graph(use_checkpoints: bool = True):
    """Create the stock analysis graph with LangGraph"""
    
    # Create the graph
    workflow = StateGraph(StockAnalysisState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("technical", technical_node)
    workflow.add_node("fundamentals", fundamentals_node)
    workflow.add_node("news", news_node)
    workflow.add_node("sec", sec_node)
    workflow.add_node("market_context", market_context_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("aggregate", aggregation_node)
    workflow.add_node("finalize", finalize_node)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add edges from initialize
    workflow.add_edge("initialize", "technical")
    
    # Parallel execution after technical analysis
    # (Technical data is needed first, then others can run in parallel)
    workflow.add_conditional_edges(
        "technical",
        route_next_agent,
        {
            "fundamentals": "fundamentals",
            "news": "news",
            "sec": "sec",
            "market_context": "market_context",
            "analyst": "analyst",
            "aggregate": "aggregate",  # If all required agents done
        }
    )
    
    # Each agent can route to others or to aggregation
    for agent in ["fundamentals", "news", "sec", "market_context", "analyst"]:
        workflow.add_conditional_edges(
            agent,
            should_continue_analysis,
            {
                "continue": route_next_agent,
                "aggregate": "aggregate",
                "fail": "finalize",
            }
        )
    
    # After aggregation, finalize
    workflow.add_edge("aggregate", "finalize")
    
    # Finalize ends the graph
    workflow.add_edge("finalize", END)
    
    # Compile with checkpointer
    if use_checkpoints:
        checkpointer = SupabaseCheckpointer()
        graph = workflow.compile(checkpointer=checkpointer)
    else:
        graph = workflow.compile()
    
    return graph


# Create the compiled graph instance
stock_analysis_graph = create_stock_analysis_graph()
```

### 3. Graph Nodes (`graph/nodes/technical_node.py`)

```python
from typing import Dict, Any
from datetime import datetime
import logging

from ..state import StockAnalysisState
from agents.technical_agent import TechnicalAgent
from stock_repository.repositories.agent_run_repository import AgentRunRepository

logger = logging.getLogger(__name__)

# Initialize agent (singleton-like)
technical_agent = TechnicalAgent()
agent_run_repo = AgentRunRepository()


async def technical_node(state: StockAnalysisState) -> Dict[str, Any]:
    """
    Node for technical analysis.
    
    LangGraph nodes receive state and return updates to state.
    """
    logger.info(f"Technical node executing for {state['ticker']}")
    
    try:
        # Execute the agent
        result = await technical_agent.run(
            ticker=state["ticker"],
            stock_id=state["stock_id"],
            analysis_run_id=state["analysis_run_id"]
        )
        
        if result.get("success"):
            return {
                "technical_data": result.get("data"),
                "completed_agents": ["technical"],  # Appends to list
                "current_step": "technical_completed",
            }
        else:
            return {
                "failed_agents": ["technical"],
                "agent_errors": {
                    "technical": result.get("error", "Unknown error")
                },
                "current_step": "technical_failed",
            }
    
    except Exception as e:
        logger.error(f"Error in technical node: {e}")
        return {
            "failed_agents": ["technical"],
            "agent_errors": {"technical": str(e)},
            "current_step": "technical_error",
        }
```

### 4. Conditional Routing (`graph/edges/router.py`)

```python
from typing import Literal
from ..state import StockAnalysisState


def route_next_agent(state: StockAnalysisState) -> str:
    """
    Decide which agent to run next based on:
    - Which agents are configured to run
    - Which agents have completed
    - Which agents have failed
    """
    
    agents_to_run = set(state["agents_to_run"])
    completed = set(state["completed_agents"])
    failed = set(state["failed_agents"])
    
    # Remove completed and failed from remaining
    remaining = agents_to_run - completed - failed
    
    # Priority order for agents
    priority_order = [
        "fundamentals",
        "news",
        "sec",
        "market_context",
        "analyst",
    ]
    
    # Find next agent to run
    for agent in priority_order:
        if agent in remaining:
            return agent
    
    # All agents done, move to aggregation
    return "aggregate"


def should_continue_analysis(state: StockAnalysisState) -> Literal["continue", "aggregate", "fail"]:
    """
    Determine if we should continue with more agents, aggregate, or fail.
    """
    
    completed = len(state["completed_agents"])
    failed = len(state["failed_agents"])
    total = len(state["agents_to_run"])
    
    # If all failed, fail the analysis
    if failed == total:
        return "fail"
    
    # If all done (completed + failed = total), aggregate
    if (completed + failed) == total:
        return "aggregate"
    
    # Otherwise continue
    return "continue"


def should_retry_agent(state: StockAnalysisState, agent_name: str) -> bool:
    """
    Determine if an agent should be retried.
    """
    
    retry_count = state.get("agent_retry_counts", {}).get(agent_name, 0)
    max_retries = state.get("max_retries", 3)
    
    return retry_count < max_retries
```

### 5. Checkpointer (`graph/checkpoints/supabase_checkpointer.py`)

```python
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Optional, Dict, Any
import json
from datetime import datetime

from stock_repository.client import get_supabase_client


class SupabaseCheckpointer(BaseCheckpointSaver):
    """
    Store LangGraph checkpoints in Supabase.
    
    This enables:
    - Pause and resume graph execution
    - Recovery from failures
    - Audit trail of execution
    """
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table_name = "langgraph_checkpoints"
    
    def put(
        self,
        config: Dict[str, Any],
        checkpoint: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save a checkpoint"""
        
        checkpoint_data = {
            "thread_id": config.get("configurable", {}).get("thread_id"),
            "checkpoint_id": checkpoint["id"],
            "parent_checkpoint_id": checkpoint.get("parent_id"),
            "checkpoint": json.dumps(checkpoint),
            "metadata": json.dumps(metadata),
            "created_at": datetime.utcnow().isoformat(),
        }
        
        response = self.client.table(self.table_name).insert(checkpoint_data).execute()
        return config
    
    def get(
        self,
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a checkpoint"""
        
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None
        
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("thread_id", thread_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        
        if response.data:
            checkpoint_row = response.data[0]
            return {
                "checkpoint": json.loads(checkpoint_row["checkpoint"]),
                "metadata": json.loads(checkpoint_row["metadata"]),
            }
        
        return None
    
    def list(
        self,
        config: Dict[str, Any],
        limit: int = 10
    ) -> list:
        """List checkpoints for a thread"""
        
        thread_id = config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return []
        
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("thread_id", thread_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        return [
            {
                "checkpoint": json.loads(row["checkpoint"]),
                "metadata": json.loads(row["metadata"]),
            }
            for row in response.data
        ]
```

### 6. Graph Service (`services/graph_service.py`)

```python
from typing import Dict, Any, Optional, AsyncIterator
from uuid import UUID
import asyncio
import logging

from graph.stock_analysis_graph import stock_analysis_graph
from graph.state import StockAnalysisState
from stock_repository.repositories.stock_repository import StockRepository
from stock_repository.repositories.analysis_repository import AnalysisRepository
from stock_repository.models.analysis import AnalysisRunCreate, RunType

logger = logging.getLogger(__name__)


class GraphService:
    """Service for executing stock analysis using LangGraph"""
    
    def __init__(self):
        self.graph = stock_analysis_graph
        self.stock_repo = StockRepository()
        self.analysis_repo = AnalysisRepository()
    
    async def analyze_stock(
        self,
        ticker: str,
        run_type: RunType = RunType.MANUAL,
        agents_to_run: Optional[list[str]] = None,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute stock analysis using LangGraph.
        
        Args:
            ticker: Stock ticker symbol
            run_type: Type of analysis run
            agents_to_run: List of agents to execute (None = all)
            thread_id: Optional thread ID for resuming from checkpoint
        """
        
        try:
            # Get stock
            stock = self.stock_repo.get_by_ticker(ticker)
            if not stock:
                raise ValueError(f"Stock {ticker} not found")
            
            # Create analysis run
            run_data = AnalysisRunCreate(
                stock_id=stock.id,
                ticker=ticker,
                run_type=run_type,
                status="pending",
                agents_total=len(agents_to_run) if agents_to_run else 8
            )
            analysis_run = self.analysis_repo.create_analysis_run(run_data)
            
            # Prepare initial state
            initial_state: StockAnalysisState = {
                "ticker": ticker,
                "stock_id": stock.id,
                "analysis_run_id": analysis_run.id,
                "run_type": run_type.value,
                "agents_to_run": agents_to_run or [
                    "technical", "fundamentals", "news", "sec",
                    "market_context", "analyst"
                ],
                "max_retries": 3,
                "technical_data": None,
                "fundamental_data": None,
                "news_data": None,
                "sec_data": None,
                "market_context_data": None,
                "analyst_data": None,
                "completed_agents": [],
                "failed_agents": [],
                "agent_errors": {},
                "aggregated_analysis": None,
                "started_at": datetime.utcnow(),
                "completed_at": None,
                "status": "running",
                "current_step": "initialize",
                "checkpoint_id": None,
                "can_resume": True,
            }
            
            # Configuration for graph execution
            config = {
                "configurable": {
                    "thread_id": thread_id or str(analysis_run.id)
                }
            }
            
            # Execute the graph
            logger.info(f"Starting graph execution for {ticker}")
            final_state = await self.graph.ainvoke(initial_state, config)
            
            # Update analysis run with results
            if final_state["status"] == "completed":
                self.analysis_repo.mark_as_completed(
                    str(analysis_run.id),
                    agents_completed=len(final_state["completed_agents"])
                )
            else:
                self.analysis_repo.mark_as_failed(
                    str(analysis_run.id),
                    error_message="Graph execution failed"
                )
            
            logger.info(f"Graph execution completed for {ticker}")
            
            return {
                "success": final_state["status"] == "completed",
                "analysis_run_id": str(analysis_run.id),
                "ticker": ticker,
                "completed_agents": final_state["completed_agents"],
                "failed_agents": final_state["failed_agents"],
                "state": final_state,
            }
            
        except Exception as e:
            logger.error(f"Error in graph execution for {ticker}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ticker": ticker
            }
    
    async def stream_analysis(
        self,
        ticker: str,
        run_type: RunType = RunType.MANUAL,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream stock analysis progress in real-time.
        
        Yields updates as each node completes.
        """
        
        # Get stock and create run (same as above)
        stock = self.stock_repo.get_by_ticker(ticker)
        analysis_run = self.analysis_repo.create_analysis_run(...)
        
        initial_state = {...}  # Same as above
        
        config = {
            "configurable": {
                "thread_id": str(analysis_run.id)
            }
        }
        
        # Stream events from graph
        async for event in self.graph.astream(initial_state, config):
            # Each event is a dict with node name and state updates
            yield {
                "event": "node_completed",
                "node": list(event.keys())[0],
                "state_updates": event,
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    async def resume_analysis(
        self,
        thread_id: str,
        analysis_run_id: UUID,
    ) -> Dict[str, Any]:
        """
        Resume a paused or failed analysis from checkpoint.
        """
        
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        # Get the last checkpoint state
        checkpoint = self.graph.get_state(config)
        
        if not checkpoint:
            raise ValueError(f"No checkpoint found for thread {thread_id}")
        
        # Resume from checkpoint
        final_state = await self.graph.ainvoke(None, config)
        
        return {
            "success": True,
            "resumed": True,
            "state": final_state,
        }
```

### 7. Updated API Endpoints (`api/jobs.py`)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from services.graph_service import GraphService
from stock_repository.models.analysis import RunType

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
graph_service = GraphService()


class TriggerAnalysisRequest(BaseModel):
    tickers: List[str]
    run_type: RunType = RunType.MANUAL
    agents: Optional[List[str]] = None


@router.post("/trigger")
async def trigger_analysis(request: TriggerAnalysisRequest):
    """Trigger stock analysis using LangGraph"""
    
    results = []
    for ticker in request.tickers:
        result = await graph_service.analyze_stock(
            ticker=ticker,
            run_type=request.run_type,
            agents_to_run=request.agents
        )
        results.append(result)
    
    return {
        "success": True,
        "results": results
    }


@router.get("/stream/{ticker}")
async def stream_analysis(ticker: str):
    """Stream analysis progress in real-time"""
    
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        async for event in graph_service.stream_analysis(ticker):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.post("/resume/{thread_id}")
async def resume_analysis(thread_id: str):
    """Resume analysis from checkpoint"""
    
    try:
        result = await graph_service.resume_analysis(thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Key Differences Summary

### Traditional Orchestrator
```python
# Old way
coordinator.analyze_stock(ticker)
  → spawns agents in parallel
  → waits for all to complete
  → aggregates results
  → returns
```

### LangGraph Orchestrator
```python
# New way
graph.ainvoke(initial_state, config)
  → flows through graph nodes
  → conditional routing based on state
  → automatic checkpointing
  → can pause/resume
  → streams intermediate results
```

---

## Benefits of LangGraph Approach

### 1. **Better Error Handling**
- Automatic retry logic
- Graceful degradation
- Resume from checkpoint on failure

### 2. **Visibility**
- See exact execution path
- Visualize the graph
- Track state at each step

### 3. **Flexibility**
- Easy to add human-in-the-loop steps
- Conditional agent execution
- Dynamic routing based on results

### 4. **Streaming**
- Real-time progress updates
- Better user experience
- Immediate feedback

### 5. **State Management**
- Centralized state
- No need for complex coordination logic
- Clear data flow

---

## Database Changes

Add checkpoint table:

```sql
CREATE TABLE langgraph_checkpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255) NOT NULL,
    parent_checkpoint_id VARCHAR(255),
    checkpoint JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(thread_id, checkpoint_id)
);

CREATE INDEX idx_checkpoints_thread_id ON langgraph_checkpoints(thread_id);
CREATE INDEX idx_checkpoints_created_at ON langgraph_checkpoints(created_at DESC);
```

---

## Updated Requirements

```txt
# requirements.txt additions

langgraph>=0.1.0
langchain>=0.1.0
langchain-core>=0.1.0
langsmith>=0.1.0  # Optional: for tracing
```

---

## Visualization Example

```python
# scripts/visualize_graph.py

from graph.stock_analysis_graph import stock_analysis_graph

# Generate Mermaid diagram
mermaid_code = stock_analysis_graph.get_graph().draw_mermaid()
print(mermaid_code)

# Or save as PNG
from langgraph.graph import draw_png
draw_png(stock_analysis_graph.get_graph(), "stock_analysis_graph.png")
```

The graph would look like:
```
[Initialize] → [Technical] → [Fundamentals]
                           ↘ [News]
                           ↘ [SEC]
                           ↘ [Market Context]
                           ↘ [Analyst]
                              ↓
                         [Aggregate] → [Finalize] → END
```

---

## Migration Path

### Phase 1: Parallel Implementation
- Keep existing orchestrator
- Implement LangGraph in parallel
- Test with subset of stocks

### Phase 2: Gradual Migration
- Use LangGraph for new features
- Migrate critical agents first
- Keep old system as fallback

### Phase 3: Full Migration
- All analyses through LangGraph
- Remove old orchestrator
- Fully leverage LangGraph features

---

## Conclusion

Using LangGraph transforms the orchestration from **imperative** (tell it how to do each step) to **declarative** (define the graph, let it execute). This provides:

- More robust error handling
- Better observability
- Easier to extend and modify
- Built-in checkpointing and resumption
- Natural streaming support

The tradeoff is additional complexity in setup and learning curve, but for a production agentic system, these benefits are well worth it.
