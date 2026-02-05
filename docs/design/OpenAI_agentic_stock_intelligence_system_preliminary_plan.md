# Agentic Stock Intelligence System – Preliminary Plan

## 1. Overview
This document outlines a preliminary design for an **agentic AI system for stock intelligence**. The system accepts a list of stocks (tickers) as input and deploys multiple specialized agents that fan out to collect, normalize, and synthesize information from diverse financial and non‑financial data sources.

The goal is to produce **actionable, evidence‑backed briefs** per stock (and optionally at the portfolio level) that combine market data, fundamentals, filings, news, and risk signals.

---

## 2. Goals and Assumptions

### Inputs
- One or more stock tickers (with optional metadata such as exchange, sector, watchlist name, or time horizon)
- User intent (e.g., daily monitoring, earnings preparation, deep‑dive research, risk review)

### Outputs
For each stock:
- Market snapshot (price, trend, volatility, volume)
- Fundamental profile (financial statements, ratios, growth)
- Events & catalysts (earnings, dividends, corporate actions)
- News & narrative summary (what happened, why it matters)
- Risk and controversy signals
- Synthesized executive summary with key drivers and open questions

### Operating Assumptions
- Data sources have heterogeneous reliability and freshness
- Numeric market data should come from authoritative APIs
- News and narrative require search‑based discovery and filtering
- Every synthesized insight must be traceable to evidence

---

## 3. High‑Level Architecture

### 3.1 Orchestrator (Supervisor Agent)
- Accepts user input and intent
- Builds a per‑ticker task graph
- Dispatches agents in parallel
- Enforces tool usage policies (rate limits, allowed sources)
- Collects and reconciles agent outputs
- Hands off evidence to the Synthesis Agent

### 3.2 Shared Infrastructure
- Tool registry (APIs, search tools, filing parsers)
- Normalization layer (maps raw outputs to a unified schema)
- Evidence store (relational DB + optional vector store)
- Scoring layer (confidence, freshness, source quality)
- Audit & logging (tool calls, timestamps, extracted facts)

---

## 4. Agents, Tools, and Information Collected

### 4.1 Market Data Agent
**Purpose:** Capture real‑time and historical price behavior.

**Typical Tools:** Market data APIs (e.g., equities price feeds, broker APIs).

**Information Collected:**
- Last price, open/high/low/close
- Percentage change and returns
- Intraday and daily time series
- Volume and liquidity indicators
- Volatility proxies (e.g., ATR, realized volatility)
- Corporate actions (splits, dividends)

---

### 4.2 Fundamentals Agent
**Purpose:** Assess financial health and valuation.

**Typical Tools:** Fundamentals and financial statement APIs.

**Information Collected:**
- Income statement, balance sheet, cash flow (annual/quarterly)
- Growth rates (revenue, EPS, free cash flow)
- Profitability and efficiency ratios
- Leverage and liquidity metrics
- Valuation multiples and historical ranges

---

### 4.3 Filings & Disclosures Agent
**Purpose:** Detect legally material changes and risks.

**Typical Tools:** SEC/EDGAR APIs, filing parsers, investor relations sites.

**Information Collected:**
- Recent 10‑K, 10‑Q, and 8‑K highlights
- Changes in risk factors and MD&A
- M&A activity, restructurings, impairments
- Share count changes and buyback programs
- Legal proceedings and regulatory disclosures

---

### 4.4 Earnings & Guidance Agent
**Purpose:** Track performance expectations and surprises.

**Typical Tools:** Earnings calendars, estimates providers, transcript sources.

**Information Collected:**
- Upcoming earnings date and time
- Historical earnings results and surprises
- Management guidance and revisions
- Consensus expectations (when available)
- Key themes from earnings calls

---

### 4.5 News & Narrative Agent
**Purpose:** Understand recent developments and market perception.

**Typical Tools:** News APIs, RSS feeds, search‑based tools (e.g., SERP extraction).

**Information Collected:**
- Recent headlines with timestamps and sources
- Event classification (earnings, M&A, regulation, product, macro)
- Entity mentions (companies, executives, competitors)
- Sentiment and narrative stance
- “What changed” vs prior state

*Note:* Search‑based tools are used primarily for discovery; original articles are stored as primary evidence.

---

### 4.6 Risk & Controversy Agent
**Purpose:** Surface non‑price downside signals.

**Typical Tools:** Search tools, filings, regulatory databases.

**Information Collected:**
- Lawsuits, investigations, and settlements
- Regulatory actions or warnings
- Governance red flags (auditor changes, restatements)
- Credit and solvency signals (when available)

---

### 4.7 Options & Positioning Agent (Optional)
**Purpose:** Gauge market expectations and hedging behavior.

**Typical Tools:** Options data APIs, broker feeds.

**Information Collected:**
- Implied volatility and skew
- Put/call volume and open interest
- Unusual options activity
- Key strikes around major events

---

### 4.8 Peer & Sector Context Agent
**Purpose:** Provide relative context.

**Typical Tools:** Sector/industry mappings, ETF data, fundamentals APIs.

**Information Collected:**
- Peer group identification
- Relative valuation and growth
- Sector and industry performance
- Spillover and correlation signals

---

## 5. Normalized Output Schema (Conceptual)

Per ticker, the system maintains:
- `ticker_profile`
- `market_snapshot`
- `fundamentals`
- `events_calendar`
- `filings_digest`
- `news_items[]`
- `risk_flags[]`
- `evidence[]` (source, URL, timestamp, confidence)

This schema enables consistent synthesis and longitudinal comparison.

---

## 6. End‑to‑End Workflow

1. User submits tickers and intent
2. Orchestrator builds task graph
3. Agents execute in parallel and collect evidence
4. Data is normalized, deduplicated, and scored
5. Synthesis Agent produces a structured stock brief
6. Results are stored for trend and change detection

---

## 7. Tooling Strategy

- Prefer authoritative APIs for numeric market data
- Use filings as the primary source for material disclosures
- Use search‑based tools for discovery, not as sole truth
- Cache aggressively based on data freshness characteristics

---

## 8. Quality and Governance Controls

- Freshness rules by data type (intraday vs quarterly)
- Cross‑source validation for critical figures
- Mandatory evidence citations for synthesis
- Source ranking and confidence scoring

---

## 9. MVP Scope (Initial Implementation)

- Orchestrator + core agents:
  - Market Data
  - Fundamentals
  - Filings
  - News & Narrative
- Unified schema and evidence logging
- Per‑ticker daily brief generator
- Basic change‑detection between runs

---

## 10. Next Steps

- Select concrete APIs and tools (free vs paid)
- Define Pydantic or JSON schemas for agent outputs
- Implement task orchestration and parallel execution
- Add alerting and monitoring triggers

---

*This document represents a preliminary design and is intended to evolve as requirements and data sources are refined.*

