# Agentic Stock Intelligence System - Architecture Document

## Document Information

- **Version:** 1.0
- **Last Updated:** February 5, 2026
- **Status:** Design Phase
- **Architecture Pattern:** Separated Pipeline + Search with Shared Repository
- **Database:** Supabase (PostgreSQL + Realtime + Auth + Storage)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Project Structure](#project-structure)
4. [Database Architecture (Supabase)](#database-architecture-supabase)
5. [Shared Repository Package](#shared-repository-package)
6. [Agent System Design](#agent-system-design)
7. [Pipeline System](#pipeline-system)
8. [Search System](#search-system)
9. [API Specifications](#api-specifications)
10. [Technology Stack](#technology-stack)
11. [Deployment Architecture](#deployment-architecture)
12. [Security & Authentication](#security--authentication)
13. [Monitoring & Observability](#monitoring--observability)
14. [Development Workflow](#development-workflow)
15. [Scaling Strategy](#scaling-strategy)

---

## System Overview

### Purpose

The Agentic Stock Intelligence System is a multi-agent platform that collects, processes, and presents comprehensive stock market analysis from multiple data sources. The system uses Supabase as the central database and a shared repository package for data access across all components.

### Key Features

- Multi-agent data collection from diverse sources
- Real-time and scheduled stock analysis
- Comprehensive technical, fundamental, and sentiment analysis
- Interactive search and visualization interface
- System monitoring and health dashboards
- Centralized data access through repository pattern
- Real-time updates via Supabase subscriptions

### Design Principles

- **Separation of Concerns:** Pipeline and Search are independent systems
- **DRY (Don't Repeat Yourself):** Shared repository package for database access
- **Single Source of Truth:** All database operations through repository layer
- **Scalability:** Each component can scale independently
- **Reliability:** Graceful degradation and error handling
- **Observability:** Comprehensive logging and monitoring

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        External Data Sources                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Twelve   │  │  Alpha   │  │   SEC    │  │  News    │  ...      │
│  │  Data    │  │ Vantage  │  │  EDGAR   │  │   API    │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
         ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Stock Intelligence Pipeline                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Agent Orchestrator                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │Technical │  │Fundament │  │   News   │  │   SEC    │  ...     │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│         ↓              ↓              ↓              ↓              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Stock Intelligence Repository Package                 │  │
│  │    (Shared DB Access Layer - Installed as dependency)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Monitoring Frontend (React)                         │  │
│  │  - Agent Status  - Job Queue  - DB Metrics  - Logs          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ Write
┌─────────────────────────────────────────────────────────────────────┐
│                         Supabase (Cloud)                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ PostgreSQL Database with Extensions:                         │  │
│  │  - PostGIS (geospatial)  - pg_cron (scheduling)             │  │
│  │  - pgvector (embeddings) - TimescaleDB (time series)        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Supabase Features:                                           │  │
│  │  - Auth  - Storage  - Realtime  - Edge Functions            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ Read
┌─────────────────────────────────────────────────────────────────────┐
│                   Stock Intelligence Search                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                Backend API (FastAPI)                          │  │
│  │  - Stock Search  - Analysis Retrieval  - Aggregations       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         Stock Intelligence Repository Package                 │  │
│  │    (Same shared package installed as dependency)             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              User Frontend (React)                            │  │
│  │  - Stock Search  - Analysis Dashboard  - Charts              │  │
│  │  - Real-time Updates via Supabase Realtime                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                          End Users
```

---

## Project Structure

### Overall Repository Structure

```
agentic_stock_intelligence/
│
├── README.md
├── docker-compose.yml              # Optional: local development setup
├── .gitignore
│
├── stock_intelligence_repository/  # SHARED REPOSITORY PACKAGE
│   ├── README.md
│   ├── setup.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   │
│   └── stock_repository/
│       ├── __init__.py
│       ├── config.py               # Supabase connection config
│       ├── client.py               # Supabase client singleton
│       │
│       ├── models/                 # Pydantic models
│       │   ├── __init__.py
│       │   ├── stock.py
│       │   ├── analysis.py
│       │   ├── agent_run.py
│       │   ├── technical_data.py
│       │   ├── fundamental_data.py
│       │   ├── news.py
│       │   └── user.py
│       │
│       ├── repositories/           # Repository pattern classes
│       │   ├── __init__.py
│       │   ├── base_repository.py
│       │   ├── stock_repository.py
│       │   ├── analysis_repository.py
│       │   ├── technical_repository.py
│       │   ├── fundamental_repository.py
│       │   ├── news_repository.py
│       │   ├── agent_run_repository.py
│       │   └── user_repository.py
│       │
│       ├── queries/                # Complex queries
│       │   ├── __init__.py
│       │   ├── search_queries.py
│       │   ├── analytics_queries.py
│       │   └── monitoring_queries.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── validators.py
│           ├── formatters.py
│           └── exceptions.py
│
├── stock_intelligence_pipeline/    # DATA COLLECTION SYSTEM
│   ├── README.md
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   ├── docker-compose.yml
│   │
│   ├── backend/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   └── logging_config.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── monitoring.py      # Agent status, metrics
│   │   │   ├── jobs.py            # Job management
│   │   │   ├── triggers.py        # Manual triggers
│   │   │   └── health.py
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py
│   │   │   ├── technical_agent.py
│   │   │   ├── fundamentals_agent.py
│   │   │   ├── news_sentiment_agent.py
│   │   │   ├── sec_filings_agent.py
│   │   │   ├── market_context_agent.py
│   │   │   ├── analyst_ratings_agent.py
│   │   │   ├── competitor_agent.py
│   │   │   └── options_agent.py
│   │   │
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py     # Main orchestration
│   │   │   ├── task_queue.py      # Celery/RQ tasks
│   │   │   └── scheduler.py       # APScheduler
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py
│   │   │   ├── twelve_data_api.py
│   │   │   ├── alpha_vantage_api.py
│   │   │   ├── finnhub_api.py
│   │   │   ├── sec_edgar_api.py
│   │   │   ├── news_api.py
│   │   │   └── yfinance_tool.py
│   │   │
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── data_cleaner.py
│   │   │   ├── aggregator.py
│   │   │   ├── enricher.py
│   │   │   └── validator.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── rate_limiter.py
│   │       ├── cache_manager.py
│   │       └── retry_helper.py
│   │
│   ├── frontend/                   # Monitoring UI
│   │   ├── package.json
│   │   ├── .env.example
│   │   │
│   │   ├── public/
│   │   │   └── index.html
│   │   │
│   │   └── src/
│   │       ├── App.jsx
│   │       ├── index.js
│   │       │
│   │       ├── components/
│   │       │   ├── AgentStatus.jsx
│   │       │   ├── JobQueue.jsx
│   │       │   ├── DBMetrics.jsx
│   │       │   ├── LogViewer.jsx
│   │       │   ├── SystemHealth.jsx
│   │       │   └── TriggerPanel.jsx
│   │       │
│   │       ├── hooks/
│   │       │   ├── useSupabaseRealtime.js
│   │       │   └── useAgentStatus.js
│   │       │
│   │       ├── services/
│   │       │   ├── api.js
│   │       │   └── supabase.js
│   │       │
│   │       └── utils/
│   │           └── formatters.js
│   │
│   ├── scripts/
│   │   ├── run_pipeline.py
│   │   └── trigger_analysis.py
│   │
│   ├── tests/
│   │   ├── test_agents/
│   │   ├── test_orchestrator/
│   │   └── test_tools/
│   │
│   └── deployment/
│       ├── Dockerfile
│       ├── kubernetes/
│       └── terraform/
│
└── stock_intelligence_search/      # USER-FACING SEARCH SYSTEM
    ├── README.md
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    ├── docker-compose.yml
    │
    ├── backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   │
    │   ├── config/
    │   │   ├── __init__.py
    │   │   └── settings.py
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── stocks.py           # Stock endpoints
    │   │   ├── search.py           # Search endpoints
    │   │   ├── analysis.py         # Analysis endpoints
    │   │   ├── compare.py          # Stock comparison
    │   │   └── health.py
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── search_service.py
    │   │   ├── analysis_service.py
    │   │   ├── chart_service.py
    │   │   └── export_service.py
    │   │
    │   └── utils/
    │       ├── __init__.py
    │       ├── cache.py
    │       └── validators.py
    │
    ├── frontend/                    # User UI
    │   ├── package.json
    │   ├── .env.example
    │   │
    │   ├── public/
    │   │   └── index.html
    │   │
    │   └── src/
    │       ├── App.jsx
    │       ├── index.js
    │       │
    │       ├── pages/
    │       │   ├── Home.jsx
    │       │   ├── StockDetail.jsx
    │       │   ├── Compare.jsx
    │       │   └── Watchlist.jsx
    │       │
    │       ├── components/
    │       │   ├── SearchBar.jsx
    │       │   ├── StockCard.jsx
    │       │   ├── TechnicalChart.jsx
    │       │   ├── FundamentalTable.jsx
    │       │   ├── NewsCard.jsx
    │       │   ├── SentimentGauge.jsx
    │       │   └── AnalysisTimeline.jsx
    │       │
    │       ├── hooks/
    │       │   ├── useStockData.js
    │       │   ├── useRealtimeUpdates.js
    │       │   └── useSearch.js
    │       │
    │       ├── services/
    │       │   ├── api.js
    │       │   └── supabase.js
    │       │
    │       └── utils/
    │           ├── formatters.js
    │           └── chartHelpers.js
    │
    ├── tests/
    │   ├── test_api/
    │   └── test_services/
    │
    └── deployment/
        ├── Dockerfile
        └── kubernetes/
```

---

## Database Architecture (Supabase)

Due to length constraints, I'll create this as a separate comprehensive document. For now, here's the summary of key tables:

### Core Tables

1. **stocks** - Master stock data
2. **analysis_runs** - Track analysis execution
3. **technical_data** - Price and technical indicators (TimescaleDB hypertable)
4. **fundamental_data** - Financial statements and ratios
5. **news_sentiment** - News articles with sentiment analysis
6. **sec_filings** - SEC filings (10-K, 10-Q, 8-K, etc.)
7. **analyst_ratings** - Analyst recommendations and price targets
8. **agent_execution_logs** - Agent performance tracking
9. **system_metrics** - System monitoring data
10. **market_context** - Market indices and economic indicators
11. **user_watchlists** - User-created watchlists (with RLS)
12. **watchlist_stocks** - Many-to-many relationship

### Key Features

- **TimescaleDB** for time-series data (technical_data, system_metrics)
- **pgvector** for semantic search (news articles)
- **Row Level Security (RLS)** for user data
- **Database functions** for complex queries
- **Triggers** for automatic timestamp updates
- **Indexes** optimized for common queries

---

## Shared Repository Package

### Purpose

The `stock_intelligence_repository` package provides centralized database access for both Pipeline and Search systems.

### Key Benefits

✅ **Single Source of Truth** - All DB operations in one place  
✅ **Type Safety** - Pydantic models ensure data consistency  
✅ **Testability** - Easy to mock for unit tests  
✅ **Maintainability** - Schema changes in one location  
✅ **Reusability** - Shared across multiple services

### Core Components

#### 1. Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
```

#### 2. Supabase Client (`client.py`)

```python
from supabase import create_client, Client

class SupabaseClient:
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(url, key)
        return cls._instance
```

#### 3. Base Repository (`repositories/base_repository.py`)

```python
class BaseRepository(Generic[T]):
    def create(self, data: Dict) -> T: ...
    def get_by_id(self, id: str) -> Optional[T]: ...
    def get_all(self, limit: int) -> List[T]: ...
    def update(self, id: str, data: Dict) -> T: ...
    def delete(self, id: str) -> bool: ...
    def count(self, filters: Dict) -> int: ...
```

#### 4. Specialized Repositories

- **StockRepository** - Stock CRUD + search
- **AnalysisRepository** - Analysis runs management
- **TechnicalRepository** - Technical data operations
- **FundamentalRepository** - Fundamental data operations
- **NewsRepository** - News and sentiment
- **AgentRunRepository** - Agent execution tracking

### Usage Example

```python
# In Pipeline Agent
from stock_repository.repositories.stock_repository import StockRepository
from stock_repository.repositories.technical_repository import TechnicalRepository

class TechnicalAgent:
    def __init__(self):
        self.stock_repo = StockRepository()
        self.technical_repo = TechnicalRepository()
    
    async def run(self, ticker: str, analysis_run_id: str):
        stock = self.stock_repo.get_by_ticker(ticker)
        # Fetch data, calculate indicators
        self.technical_repo.bulk_create(technical_records)
```

```python
# In Search API
from stock_repository.repositories.stock_repository import StockRepository

@router.get("/stocks/{ticker}")
async def get_stock(ticker: str):
    stock_repo = StockRepository()
    stock = stock_repo.get_with_latest_price(ticker)
    return stock
```

---

## Agent System Design

### Agent Architecture

Each agent:
1. Inherits from `BaseAgent`
2. Implements `async def run()` method
3. Uses tools to fetch data
4. Stores results via repository package
5. Logs execution details

### Base Agent

```python
class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_run_repo = AgentRunRepository()
    
    async def execute(self, ticker, stock_id, analysis_run_id):
        log_id = self._create_execution_log(...)
        try:
            result = await self.run(ticker, stock_id, analysis_run_id)
            self._complete_execution_log(log_id, result)
            return result
        except Exception as e:
            self._fail_execution_log(log_id, str(e))
            return {"success": False, "error": str(e)}
    
    @abstractmethod
    async def run(self, ticker, stock_id, analysis_run_id):
        pass
```

### Agent Implementations

**Technical Agent** - Price data + indicators (RSI, MACD, etc.)  
**Fundamentals Agent** - Financial statements, ratios  
**News Sentiment Agent** - News articles + sentiment analysis  
**SEC Filings Agent** - 10-K, 10-Q, 8-K, insider trading  
**Market Context Agent** - Market indices, economic indicators  
**Analyst Ratings Agent** - Analyst recommendations  
**Competitor Agent** - Peer comparison  
**Options Agent** - Options flow, put/call ratios

---

## Pipeline System

### Coordinator

Orchestrates agent execution:

```python
class Coordinator:
    def __init__(self):
        self.stock_repo = StockRepository()
        self.analysis_repo = AnalysisRepository()
        self.agents = {
            "technical": TechnicalAgent(),
            "fundamentals": FundamentalsAgent(),
            # ... more agents
        }
    
    async def analyze_stock(self, ticker, run_type):
        # Create analysis run
        analysis_run = self.analysis_repo.create_analysis_run(...)
        
        # Run agents in parallel
        tasks = [agent.execute(...) for agent in self.agents.values()]
        results = await asyncio.gather(*tasks)
        
        # Update run status
        self.analysis_repo.mark_as_completed(...)
        
        return results
```

### Scheduler

Uses APScheduler for periodic analysis:

```python
scheduler = AsyncIOScheduler()

# Daily analysis at market close
scheduler.add_job(
    daily_analysis,
    CronTrigger(hour=22, minute=0),
    id="daily_analysis"
)

scheduler.start()
```

### Monitoring Frontend

React dashboard showing:
- Live agent status
- Job queue
- Database metrics
- System health
- Error logs

Uses Supabase Realtime for live updates.

---

## Search System

### Backend API (FastAPI)

```python
# Stock endpoints
GET  /api/stocks/search
GET  /api/stocks/{ticker}
GET  /api/stocks/{ticker}/technical
GET  /api/stocks/{ticker}/fundamentals
GET  /api/stocks/{ticker}/news

# Analysis endpoints
GET  /api/analysis/{ticker}
GET  /api/analysis/{ticker}/history

# Watchlist endpoints
POST /api/watchlist
GET  /api/watchlist/{id}
```

### Frontend (React)

Pages:
- **Home** - Search and trending stocks
- **StockDetail** - Comprehensive analysis view
- **Compare** - Side-by-side comparison
- **Watchlist** - User's saved stocks

Components:
- TechnicalChart (price chart with indicators)
- FundamentalTable (financial metrics)
- NewsCard (news with sentiment)
- SentimentGauge (visual sentiment indicator)

Uses React Query for data fetching and Supabase Realtime for live updates.

---

## Technology Stack

### Backend
- Python 3.10+, FastAPI
- Supabase (PostgreSQL)
- Celery + Redis (task queue)
- APScheduler (scheduling)
- Pydantic (validation)

### Frontend
- React 18+, Vite
- Tailwind CSS + shadcn/ui
- React Query, Zustand
- Recharts (charting)
- Supabase JS (realtime)

### Database
- Supabase (managed PostgreSQL)
- TimescaleDB (time-series)
- pgvector (embeddings)
- PostGIS (geospatial)

### External APIs
- Twelve Data (primary)
- Alpha Vantage (backup)
- Financial Modeling Prep
- News API, Finnhub
- SEC EDGAR

---

## Deployment Architecture

### Production

```
Load Balancer (AWS ALB)
    ↓              ↓
Pipeline       Search
(ECS)          (ECS)
    ↓              ↓
Supabase Cloud + Redis (ElastiCache)
```

### Environment Variables

**Repository Package:**
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
DATABASE_URL=postgresql://...
```

**Pipeline:**
```bash
# APIs
TWELVE_DATA_API_KEY=xxx
ALPHA_VANTAGE_API_KEY=xxx
FINNHUB_API_KEY=xxx

# Queue
REDIS_URL=redis://localhost:6379

# Scheduler
ENABLE_SCHEDULER=true
```

**Search:**
```bash
SUPABASE_KEY=xxx  # anon key
CORS_ORIGINS=https://app.example.com
```

---

## Security & Authentication

### Supabase Auth

```python
async def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    user = supabase.auth.get_user(token)
    return user
```

### Row Level Security

```sql
CREATE POLICY "Users can view their watchlists"
ON user_watchlists FOR SELECT
USING (auth.uid() = user_id);
```

### API Keys

- Store in environment variables
- Use Supabase Vault for secrets
- Rotate regularly
- Rate limit per API

---

## Monitoring & Observability

### Logging

Structured JSON logging:
```python
logger.info("Agent completed", extra={
    "agent": "technical",
    "ticker": "AAPL",
    "duration": 45,
    "records": 30
})
```

### Metrics

Store in `system_metrics` table:
- Agent performance
- API usage
- Database stats
- Error rates

### Health Checks

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "components": {
            "supabase": "healthy",
            "redis": "healthy"
        }
    }
```

### Dashboard

Pipeline frontend shows:
- Agent status (running/completed/failed)
- Job queue length
- API call counts
- Database metrics
- Recent errors

Real-time updates via Supabase Realtime.

---

## Development Workflow

### Setup

```bash
# 1. Clone repo
git clone <repo>

# 2. Setup Supabase (via dashboard)
# - Create project
# - Run schema SQL
# - Get credentials

# 3. Install repository package
cd stock_intelligence_repository
pip install -e .

# 4. Setup Pipeline
cd ../stock_intelligence_pipeline/backend
pip install -r requirements.txt

# 5. Setup Search
cd ../../stock_intelligence_search/backend
pip install -r requirements.txt

# 6. Run with Docker Compose
docker-compose up
```

### Running Locally

```bash
# Pipeline
cd pipeline/backend
uvicorn main:app --reload --port 8000

cd pipeline/frontend
npm run dev

# Search
cd search/backend
uvicorn main:app --reload --port 8001

cd search/frontend
npm run dev
```

---

## Scaling Strategy

### Horizontal Scaling

**Pipeline:** Scale workers based on queue length  
**Search:** Scale API servers based on traffic

### Database Scaling

- Read replicas for Search system
- Connection pooling
- Query optimization
- Partitioning for time-series data

### Caching

```python
# L1: In-memory (per instance)
@lru_cache(maxsize=1000)
def get_stock(ticker): ...

# L2: Redis (shared)
async def get_with_cache(ticker):
    cached = await redis.get(f"stock:{ticker}")
    if cached:
        return cached
    data = fetch_from_db(ticker)
    await redis.setex(f"stock:{ticker}", 300, data)
    return data
```

---

## Next Steps

1. ✅ Architecture designed
2. ⬜ Set up Supabase project
3. ⬜ Implement repository package
4. ⬜ Build Phase 1 agents
5. ⬜ Develop Pipeline UI
6. ⬜ Create Search frontend
7. ⬜ Deploy to staging

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Architecture Pattern:** CVE Intelligence inspired (Pipeline + Search)  
**Database:** Supabase with shared repository package
