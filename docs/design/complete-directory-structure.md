# Agentic Stock Intelligence System - Complete Directory Structure
## Production-Ready with LangGraph & Docker

---

## Complete Project Structure

```
agentic_stock_intelligence/
│
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml                      # Local development
├── docker-compose.prod.yml                 # Production deployment
├── .env.example
├── Makefile                                # Common commands
│
├── docs/
│   ├── architecture.md
│   ├── setup-guide.md
│   ├── api-reference.md
│   ├── deployment-guide.md
│   └── langgraph-guide.md
│
├── infrastructure/                         # Infrastructure as Code
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── supabase.tf
│   │   ├── aws.tf
│   │   └── redis.tf
│   │
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── pipeline/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── ingress.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── secrets.yaml
│   │   │
│   │   └── search/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── ingress.yaml
│   │       ├── configmap.yaml
│   │       └── secrets.yaml
│   │
│   └── docker/
│       └── nginx/
│           ├── Dockerfile
│           └── nginx.conf
│
├── scripts/
│   ├── setup-dev.sh
│   ├── deploy-prod.sh
│   ├── backup-db.sh
│   ├── run-migrations.sh
│   └── health-check.sh
│
│
├── stock_intelligence_repository/          # ═══════════════════════════
│   │                                        # SHARED REPOSITORY PACKAGE
│   ├── README.md                            # ═══════════════════════════
│   ├── setup.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── MANIFEST.in
│   │
│   ├── stock_repository/
│   │   ├── __init__.py
│   │   ├── version.py
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py
│   │   │
│   │   ├── client/
│   │   │   ├── __init__.py
│   │   │   ├── supabase_client.py
│   │   │   └── redis_client.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── stock.py
│   │   │   ├── analysis.py
│   │   │   ├── agent_run.py
│   │   │   ├── technical_data.py
│   │   │   ├── fundamental_data.py
│   │   │   ├── news.py
│   │   │   ├── sec_filings.py
│   │   │   ├── analyst_ratings.py
│   │   │   ├── market_context.py
│   │   │   ├── system_metrics.py
│   │   │   └── user.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py
│   │   │   ├── stock_repository.py
│   │   │   ├── analysis_repository.py
│   │   │   ├── technical_repository.py
│   │   │   ├── fundamental_repository.py
│   │   │   ├── news_repository.py
│   │   │   ├── sec_repository.py
│   │   │   ├── analyst_repository.py
│   │   │   ├── agent_run_repository.py
│   │   │   ├── metrics_repository.py
│   │   │   └── checkpoint_repository.py
│   │   │
│   │   ├── queries/
│   │   │   ├── __init__.py
│   │   │   ├── search_queries.py
│   │   │   ├── analytics_queries.py
│   │   │   ├── monitoring_queries.py
│   │   │   └── aggregation_queries.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       ├── exceptions.py
│   │       └── helpers.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_models/
│   │   ├── test_repositories/
│   │   └── test_queries/
│   │
│   └── migrations/
│       ├── versions/
│       └── alembic.ini
│
│
├── stock_intelligence_pipeline/            # ═══════════════════════════
│   │                                        # DATA COLLECTION SYSTEM
│   ├── README.md                            # WITH LANGGRAPH
│   ├── .env.example                         # ═══════════════════════════
│   ├── .gitignore
│   ├── .dockerignore
│   ├── Dockerfile                           # Backend Docker image
│   ├── docker-compose.yml                   # Local dev
│   ├── requirements.txt
│   ├── setup.py
│   │
│   ├── backend/
│   │   ├── main.py                          # FastAPI application
│   │   ├── requirements.txt
│   │   ├── pyproject.toml
│   │   ├── __init__.py
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py                  # Pydantic settings
│   │   │   ├── logging_config.py
│   │   │   └── constants.py
│   │   │
│   │   ├── api/                             # FastAPI routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                      # Dependencies
│   │   │   ├── middleware.py
│   │   │   │
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── monitoring.py            # System monitoring
│   │   │   │   ├── jobs.py                  # Job management
│   │   │   │   ├── triggers.py              # Manual triggers
│   │   │   │   ├── graphs.py                # Graph execution
│   │   │   │   ├── checkpoints.py           # Checkpoint management
│   │   │   │   ├── agents.py                # Agent info
│   │   │   │   ├── health.py                # Health checks
│   │   │   │   └── websocket.py             # WebSocket for streaming
│   │   │
│   │   ├── graph/                           # ═══ LANGGRAPH ═══
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── state/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stock_analysis_state.py  # Main state schema
│   │   │   │   ├── agent_state.py           # Agent-specific states
│   │   │   │   └── error_state.py           # Error handling state
│   │   │   │
│   │   │   ├── nodes/                       # Graph nodes (agents)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_node.py
│   │   │   │   ├── initialize_node.py       # Initialize analysis
│   │   │   │   ├── technical_node.py        # Technical analysis
│   │   │   │   ├── fundamentals_node.py     # Fundamental analysis
│   │   │   │   ├── news_node.py             # News & sentiment
│   │   │   │   ├── sec_node.py              # SEC filings
│   │   │   │   ├── market_context_node.py   # Market context
│   │   │   │   ├── analyst_node.py          # Analyst ratings
│   │   │   │   ├── competitor_node.py       # Competitor analysis
│   │   │   │   ├── options_node.py          # Options data
│   │   │   │   ├── aggregation_node.py      # Aggregate results
│   │   │   │   ├── validation_node.py       # Validate data
│   │   │   │   ├── error_handler_node.py    # Error handling
│   │   │   │   └── finalize_node.py         # Finalize & persist
│   │   │   │
│   │   │   ├── edges/                       # Conditional routing
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py                # Main routing logic
│   │   │   │   ├── conditions.py            # Routing conditions
│   │   │   │   ├── retry_logic.py           # Retry strategies
│   │   │   │   └── priority.py              # Agent priorities
│   │   │   │
│   │   │   ├── graphs/                      # Graph definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stock_analysis_graph.py  # Main graph
│   │   │   │   ├── quick_analysis_graph.py  # Quick analysis (subset)
│   │   │   │   └── deep_analysis_graph.py   # Deep analysis (all agents)
│   │   │   │
│   │   │   ├── checkpoints/                 # Checkpoint management
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_checkpointer.py
│   │   │   │   ├── supabase_checkpointer.py # Supabase checkpoint saver
│   │   │   │   ├── memory_checkpointer.py   # In-memory (dev)
│   │   │   │   └── redis_checkpointer.py    # Redis (production)
│   │   │   │
│   │   │   └── tools/                       # LangGraph tools
│   │   │       ├── __init__.py
│   │   │       ├── base_tool.py
│   │   │       └── graph_tools.py           # Helper tools for graph
│   │   │
│   │   ├── agents/                          # Agent implementations
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
│   │   ├── tools/                           # External API tools
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py
│   │   │   │
│   │   │   ├── data_providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── twelve_data_tool.py
│   │   │   │   ├── alpha_vantage_tool.py
│   │   │   │   ├── finnhub_tool.py
│   │   │   │   ├── fmp_tool.py              # Financial Modeling Prep
│   │   │   │   ├── sec_edgar_tool.py
│   │   │   │   ├── news_api_tool.py
│   │   │   │   └── yfinance_tool.py
│   │   │   │
│   │   │   └── utilities/
│   │   │       ├── __init__.py
│   │   │       ├── rate_limiter_tool.py
│   │   │       ├── cache_tool.py
│   │   │       └── validator_tool.py
│   │   │
│   │   ├── processors/                      # Data processors
│   │   │   ├── __init__.py
│   │   │   ├── base_processor.py
│   │   │   ├── data_cleaner.py
│   │   │   ├── aggregator.py
│   │   │   ├── enricher.py
│   │   │   ├── validator.py
│   │   │   ├── normalizer.py
│   │   │   └── transformer.py
│   │   │
│   │   ├── services/                        # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── graph_service.py             # Graph execution service
│   │   │   ├── checkpoint_service.py        # Checkpoint management
│   │   │   ├── scheduler_service.py         # Job scheduling
│   │   │   ├── monitoring_service.py        # System monitoring
│   │   │   ├── notification_service.py      # Notifications
│   │   │   └── cache_service.py             # Caching layer
│   │   │
│   │   ├── workers/                         # Background workers
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py                # Celery configuration
│   │   │   ├── tasks.py                     # Celery tasks
│   │   │   ├── scheduled_tasks.py           # Scheduled jobs
│   │   │   └── monitoring_tasks.py          # Monitoring tasks
│   │   │
│   │   ├── core/                            # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── cache_manager.py
│   │   │   ├── retry_helper.py
│   │   │   ├── error_handler.py
│   │   │   └── metrics.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── decorators.py
│   │       ├── validators.py
│   │       └── helpers.py
│   │
│   ├── frontend/                            # ═══ MONITORING UI ═══
│   │   ├── Dockerfile                       # Frontend Docker image
│   │   ├── .dockerignore
│   │   ├── package.json
│   │   ├── package-lock.json
│   │   ├── vite.config.js
│   │   ├── tsconfig.json
│   │   ├── .env.example
│   │   ├── .eslintrc.js
│   │   ├── .prettierrc
│   │   │
│   │   ├── public/
│   │   │   ├── index.html
│   │   │   ├── favicon.ico
│   │   │   └── manifest.json
│   │   │
│   │   ├── src/
│   │   │   ├── main.tsx
│   │   │   ├── App.tsx
│   │   │   ├── vite-env.d.ts
│   │   │   │
│   │   │   ├── pages/
│   │   │   │   ├── Dashboard.tsx            # Main dashboard
│   │   │   │   ├── GraphExecution.tsx       # Graph execution view
│   │   │   │   ├── AgentStatus.tsx          # Agent status page
│   │   │   │   ├── JobQueue.tsx             # Job queue page
│   │   │   │   ├── Checkpoints.tsx          # Checkpoint viewer
│   │   │   │   ├── Metrics.tsx              # System metrics
│   │   │   │   ├── Logs.tsx                 # Log viewer
│   │   │   │   └── Settings.tsx             # Settings
│   │   │   │
│   │   │   ├── components/
│   │   │   │   ├── common/
│   │   │   │   │   ├── Button.tsx
│   │   │   │   │   ├── Card.tsx
│   │   │   │   │   ├── Modal.tsx
│   │   │   │   │   ├── Table.tsx
│   │   │   │   │   └── Loading.tsx
│   │   │   │   │
│   │   │   │   ├── monitoring/
│   │   │   │   │   ├── SystemHealth.tsx
│   │   │   │   │   ├── AgentStatusCard.tsx
│   │   │   │   │   ├── JobQueueTable.tsx
│   │   │   │   │   ├── MetricsChart.tsx
│   │   │   │   │   ├── DBMetrics.tsx
│   │   │   │   │   └── APIUsage.tsx
│   │   │   │   │
│   │   │   │   ├── graph/
│   │   │   │   │   ├── GraphVisualizer.tsx  # LangGraph visualization
│   │   │   │   │   ├── NodeDetail.tsx       # Node details
│   │   │   │   │   ├── EdgeFlow.tsx         # Edge visualization
│   │   │   │   │   ├── StateViewer.tsx      # State inspection
│   │   │   │   │   └── ExecutionTimeline.tsx
│   │   │   │   │
│   │   │   │   ├── jobs/
│   │   │   │   │   ├── TriggerPanel.tsx
│   │   │   │   │   ├── JobStatusCard.tsx
│   │   │   │   │   ├── JobDetails.tsx
│   │   │   │   │   └── CheckpointList.tsx
│   │   │   │   │
│   │   │   │   └── logs/
│   │   │   │       ├── LogViewer.tsx
│   │   │   │       ├── LogFilter.tsx
│   │   │   │       └── LogEntry.tsx
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   ├── useSupabaseRealtime.ts
│   │   │   │   ├── useAgentStatus.ts
│   │   │   │   ├── useJobQueue.ts
│   │   │   │   ├── useGraphExecution.ts
│   │   │   │   ├── useCheckpoints.ts
│   │   │   │   ├── useMetrics.ts
│   │   │   │   └── useWebSocket.ts
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── api.ts                   # API client
│   │   │   │   ├── supabase.ts              # Supabase client
│   │   │   │   └── websocket.ts             # WebSocket client
│   │   │   │
│   │   │   ├── store/                       # State management
│   │   │   │   ├── index.ts
│   │   │   │   ├── agentStore.ts
│   │   │   │   ├── jobStore.ts
│   │   │   │   ├── metricsStore.ts
│   │   │   │   └── settingsStore.ts
│   │   │   │
│   │   │   ├── types/
│   │   │   │   ├── index.ts
│   │   │   │   ├── agent.ts
│   │   │   │   ├── job.ts
│   │   │   │   ├── graph.ts
│   │   │   │   └── metrics.ts
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── formatters.ts
│   │   │   │   ├── validators.ts
│   │   │   │   └── helpers.ts
│   │   │   │
│   │   │   └── styles/
│   │   │       ├── index.css
│   │   │       └── tailwind.css
│   │   │
│   │   └── nginx/
│   │       └── nginx.conf                   # Production nginx config
│   │
│   ├── scripts/
│   │   ├── start.sh
│   │   ├── run_analysis.py
│   │   ├── trigger_analysis.py
│   │   ├── visualize_graph.py
│   │   ├── export_checkpoints.py
│   │   └── cleanup.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   │
│   │   ├── unit/
│   │   │   ├── test_agents/
│   │   │   ├── test_tools/
│   │   │   ├── test_processors/
│   │   │   └── test_services/
│   │   │
│   │   ├── integration/
│   │   │   ├── test_graph/
│   │   │   │   ├── test_graph_execution.py
│   │   │   │   ├── test_nodes.py
│   │   │   │   ├── test_edges.py
│   │   │   │   ├── test_checkpoints.py
│   │   │   │   └── test_state_flow.py
│   │   │   │
│   │   │   ├── test_api/
│   │   │   └── test_workers/
│   │   │
│   │   └── e2e/
│   │       └── test_full_pipeline.py
│   │
│   └── deployment/
│       ├── docker/
│       │   ├── backend.Dockerfile
│       │   ├── frontend.Dockerfile
│       │   ├── worker.Dockerfile
│       │   └── .dockerignore
│       │
│       ├── kubernetes/
│       │   ├── deployment-backend.yaml
│       │   ├── deployment-frontend.yaml
│       │   ├── deployment-worker.yaml
│       │   ├── service.yaml
│       │   ├── ingress.yaml
│       │   ├── configmap.yaml
│       │   ├── secrets.yaml
│       │   ├── hpa.yaml                     # Horizontal Pod Autoscaler
│       │   └── cronjob.yaml                 # Scheduled jobs
│       │
│       └── helm/
│           └── pipeline/
│               ├── Chart.yaml
│               ├── values.yaml
│               └── templates/
│
│
└── stock_intelligence_search/              # ═══════════════════════════
    │                                        # USER-FACING SEARCH SYSTEM
    ├── README.md                            # ═══════════════════════════
    ├── .env.example
    ├── .gitignore
    ├── .dockerignore
    ├── Dockerfile                           # Backend Docker image
    ├── docker-compose.yml
    ├── requirements.txt
    │
    ├── backend/
    │   ├── main.py                          # FastAPI application
    │   ├── requirements.txt
    │   ├── __init__.py
    │   │
    │   ├── config/
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── logging_config.py
    │   │   └── constants.py
    │   │
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── deps.py                      # Dependencies
    │   │   ├── middleware.py
    │   │   │
    │   │   ├── v1/
    │   │   │   ├── __init__.py
    │   │   │   ├── stocks.py                # Stock endpoints
    │   │   │   ├── search.py                # Search endpoints
    │   │   │   ├── analysis.py              # Analysis endpoints
    │   │   │   ├── technical.py             # Technical data
    │   │   │   ├── fundamentals.py          # Fundamental data
    │   │   │   ├── news.py                  # News endpoints
    │   │   │   ├── compare.py               # Stock comparison
    │   │   │   ├── watchlist.py             # User watchlists
    │   │   │   ├── auth.py                  # Authentication
    │   │   │   └── health.py                # Health checks
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── search_service.py
    │   │   ├── analysis_service.py
    │   │   ├── stock_service.py
    │   │   ├── chart_service.py
    │   │   ├── comparison_service.py
    │   │   ├── watchlist_service.py
    │   │   ├── export_service.py
    │   │   └── cache_service.py
    │   │
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── security.py                  # Auth utilities
    │   │   ├── cache.py
    │   │   └── pagination.py
    │   │
    │   └── utils/
    │       ├── __init__.py
    │       ├── logger.py
    │       ├── validators.py
    │       ├── formatters.py
    │       └── helpers.py
    │
    ├── frontend/                            # ═══ USER-FACING UI ═══
    │   ├── Dockerfile                       # Frontend Docker image
    │   ├── .dockerignore
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── vite.config.js
    │   ├── tsconfig.json
    │   ├── .env.example
    │   ├── .eslintrc.js
    │   ├── .prettierrc
    │   │
    │   ├── public/
    │   │   ├── index.html
    │   │   ├── favicon.ico
    │   │   ├── logo192.png
    │   │   └── manifest.json
    │   │
    │   ├── src/
    │   │   ├── main.tsx
    │   │   ├── App.tsx
    │   │   ├── vite-env.d.ts
    │   │   │
    │   │   ├── pages/
    │   │   │   ├── Home.tsx                 # Homepage with search
    │   │   │   ├── StockDetail.tsx          # Stock detail page
    │   │   │   ├── Compare.tsx              # Stock comparison
    │   │   │   ├── Watchlist.tsx            # User watchlists
    │   │   │   ├── Screener.tsx             # Stock screener
    │   │   │   ├── Portfolio.tsx            # Portfolio tracking
    │   │   │   ├── News.tsx                 # News feed
    │   │   │   ├── Login.tsx                # Login page
    │   │   │   └── Profile.tsx              # User profile
    │   │   │
    │   │   ├── components/
    │   │   │   ├── common/
    │   │   │   │   ├── Button.tsx
    │   │   │   │   ├── Card.tsx
    │   │   │   │   ├── Modal.tsx
    │   │   │   │   ├── Table.tsx
    │   │   │   │   ├── Tabs.tsx
    │   │   │   │   └── Loading.tsx
    │   │   │   │
    │   │   │   ├── layout/
    │   │   │   │   ├── Header.tsx
    │   │   │   │   ├── Sidebar.tsx
    │   │   │   │   ├── Footer.tsx
    │   │   │   │   └── Layout.tsx
    │   │   │   │
    │   │   │   ├── search/
    │   │   │   │   ├── SearchBar.tsx
    │   │   │   │   ├── SearchResults.tsx
    │   │   │   │   ├── SearchFilters.tsx
    │   │   │   │   └── RecentSearches.tsx
    │   │   │   │
    │   │   │   ├── stock/
    │   │   │   │   ├── StockCard.tsx
    │   │   │   │   ├── StockHeader.tsx
    │   │   │   │   ├── StockOverview.tsx
    │   │   │   │   ├── PriceDisplay.tsx
    │   │   │   │   └── StockList.tsx
    │   │   │   │
    │   │   │   ├── charts/
    │   │   │   │   ├── TechnicalChart.tsx
    │   │   │   │   ├── CandlestickChart.tsx
    │   │   │   │   ├── VolumeChart.tsx
    │   │   │   │   ├── IndicatorChart.tsx
    │   │   │   │   └── ComparisonChart.tsx
    │   │   │   │
    │   │   │   ├── analysis/
    │   │   │   │   ├── AnalysisSummary.tsx
    │   │   │   │   ├── AnalysisTimeline.tsx
    │   │   │   │   ├── TechnicalAnalysis.tsx
    │   │   │   │   ├── FundamentalTable.tsx
    │   │   │   │   ├── FinancialMetrics.tsx
    │   │   │   │   ├── SentimentGauge.tsx
    │   │   │   │   └── AnalystRatings.tsx
    │   │   │   │
    │   │   │   ├── news/
    │   │   │   │   ├── NewsCard.tsx
    │   │   │   │   ├── NewsFeed.tsx
    │   │   │   │   ├── NewsFilter.tsx
    │   │   │   │   └── SentimentBadge.tsx
    │   │   │   │
    │   │   │   ├── watchlist/
    │   │   │   │   ├── WatchlistCard.tsx
    │   │   │   │   ├── WatchlistGrid.tsx
    │   │   │   │   ├── AddToWatchlist.tsx
    │   │   │   │   └── WatchlistStocks.tsx
    │   │   │   │
    │   │   │   └── comparison/
    │   │   │       ├── ComparisonTable.tsx
    │   │   │       ├── ComparisonMetrics.tsx
    │   │   │       └── StockSelector.tsx
    │   │   │
    │   │   ├── hooks/
    │   │   │   ├── useStockData.ts
    │   │   │   ├── useRealtimeUpdates.ts
    │   │   │   ├── useSearch.ts
    │   │   │   ├── useAnalysis.ts
    │   │   │   ├── useWatchlist.ts
    │   │   │   ├── useAuth.ts
    │   │   │   └── useChartData.ts
    │   │   │
    │   │   ├── services/
    │   │   │   ├── api.ts                   # API client
    │   │   │   ├── supabase.ts              # Supabase client
    │   │   │   └── auth.ts                  # Auth service
    │   │   │
    │   │   ├── store/                       # Zustand stores
    │   │   │   ├── index.ts
    │   │   │   ├── stockStore.ts
    │   │   │   ├── searchStore.ts
    │   │   │   ├── watchlistStore.ts
    │   │   │   ├── userStore.ts
    │   │   │   └── settingsStore.ts
    │   │   │
    │   │   ├── types/
    │   │   │   ├── index.ts
    │   │   │   ├── stock.ts
    │   │   │   ├── analysis.ts
    │   │   │   ├── chart.ts
    │   │   │   └── user.ts
    │   │   │
    │   │   ├── utils/
    │   │   │   ├── formatters.ts
    │   │   │   ├── validators.ts
    │   │   │   ├── chartHelpers.ts
    │   │   │   └── helpers.ts
    │   │   │
    │   │   └── styles/
    │   │       ├── index.css
    │   │       └── tailwind.css
    │   │
    │   └── nginx/
    │       └── nginx.conf
    │
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   │
    │   ├── unit/
    │   │   ├── test_services/
    │   │   └── test_utils/
    │   │
    │   ├── integration/
    │   │   └── test_api/
    │   │
    │   └── e2e/
    │       └── test_user_flows.py
    │
    └── deployment/
        ├── docker/
        │   ├── backend.Dockerfile
        │   ├── frontend.Dockerfile
        │   └── .dockerignore
        │
        ├── kubernetes/
        │   ├── deployment-backend.yaml
        │   ├── deployment-frontend.yaml
        │   ├── service.yaml
        │   ├── ingress.yaml
        │   ├── configmap.yaml
        │   ├── secrets.yaml
        │   └── hpa.yaml
        │
        └── helm/
            └── search/
                ├── Chart.yaml
                ├── values.yaml
                └── templates/
```

---

## Summary Statistics

### Total Structure
- **3 Main Systems**: Repository, Pipeline, Search
- **6 Docker Images**: Repository (not dockerized), Pipeline Backend, Pipeline Frontend, Pipeline Worker, Search Backend, Search Frontend
- **Multiple Deployment Options**: Docker Compose (dev), Kubernetes (prod), Helm Charts

### Pipeline System (with LangGraph)
- **Backend**: FastAPI + LangGraph orchestration
- **Frontend**: React monitoring dashboard
- **Workers**: Celery for background tasks
- **Key Features**: 
  - Graph-based agent orchestration
  - Checkpoint management
  - Real-time streaming
  - WebSocket support

### Search System
- **Backend**: FastAPI REST API
- **Frontend**: React user interface
- **Key Features**:
  - Stock search and analysis
  - Real-time updates (Supabase)
  - Interactive charts
  - User watchlists

### Deployment
- **Development**: Docker Compose for local setup
- **Production**: Kubernetes with Helm charts
- **Infrastructure**: Terraform for IaC
- **Monitoring**: Integrated monitoring and logging
