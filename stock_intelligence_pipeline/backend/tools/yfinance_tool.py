"""
YFinance Tool - Wrapper around yfinance library for stock data retrieval

This tool provides methods for fetching:
- Company info and profile
- Financial statements (income, balance sheet, cash flow)
- Historical price data
- Analyst recommendations
- Key financial ratios

Used by multiple agents (fundamental, technical, etc.)
"""
import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class YFinanceTool:
    """
    Wrapper around yfinance for structured data retrieval.
    
    Each method fetches a specific type of data and returns
    a clean dict. Agents call the methods they need.
    """
    
    def __init__(self):
        self._cache = {}  # Simple in-memory cache to avoid duplicate API calls
    
    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get or create a yfinance Ticker object (cached)"""
        if symbol not in self._cache:
            self._cache[symbol] = yf.Ticker(symbol)
        return self._cache[symbol]
    
    # ==========================================
    # Company Information
    # ==========================================
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic company information and profile.
        
        Returns: company name, sector, industry, description, market cap, etc.
        """
        ticker = self._get_ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName") or info.get("shortName", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "description": info.get("longBusinessSummary", ""),
            "website": info.get("website", ""),
            "country": info.get("country", "Unknown"),
            "exchange": info.get("exchange", "Unknown"),
            "currency": info.get("currency", "USD"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "employees": info.get("fullTimeEmployees"),
        }
    
    # ==========================================
    # Financial Ratios & Valuation
    # ==========================================
    
    def get_key_ratios(self, symbol: str) -> Dict[str, Any]:
        """
        Get key financial ratios and valuation metrics.
        
        Returns: P/E, P/B, P/S, EV/EBITDA, ROE, ROA, margins, etc.
        """
        ticker = self._get_ticker(symbol)
        info = ticker.info
        
        return {
            # Valuation ratios
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_to_ebitda": info.get("enterpriseToEbitda"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            
            # Profitability
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "gross_margin": info.get("grossMargins"),
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            
            # Per share
            "eps_trailing": info.get("trailingEps"),
            "eps_forward": info.get("forwardEps"),
            "book_value_per_share": info.get("bookValue"),
            "revenue_per_share": info.get("revenuePerShare"),
            
            # Dividends
            "dividend_yield": info.get("dividendYield"),
            "dividend_rate": info.get("dividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            
            # Debt
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            
            # Growth
            "earnings_growth": info.get("earningsGrowth"),
            "revenue_growth": info.get("revenueGrowth"),
        }
    
    # ==========================================
    # Financial Statements
    # ==========================================
    
    def get_income_statement(self, symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get income statement data.
        
        Returns: revenue, net income, EPS, margins for recent periods
        """
        ticker = self._get_ticker(symbol)
        
        if quarterly:
            stmt = ticker.quarterly_income_stmt
        else:
            stmt = ticker.income_stmt
        
        if stmt is None or stmt.empty:
            return {"periods": [], "error": "No income statement data available"}
        
        periods = []
        for col in stmt.columns[:4]:  # Last 4 periods
            period_data = {}
            for row in stmt.index:
                value = stmt.loc[row, col]
                # Convert numpy types to Python native types
                if hasattr(value, 'item'):
                    value = value.item()
                period_data[str(row)] = value
            
            periods.append({
                "period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col),
                "data": period_data
            })
        
        return {
            "type": "quarterly" if quarterly else "annual",
            "periods": periods
        }
    
    def get_balance_sheet(self, symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get balance sheet data.
        
        Returns: assets, liabilities, equity for recent periods
        """
        ticker = self._get_ticker(symbol)
        
        if quarterly:
            stmt = ticker.quarterly_balance_sheet
        else:
            stmt = ticker.balance_sheet
        
        if stmt is None or stmt.empty:
            return {"periods": [], "error": "No balance sheet data available"}
        
        periods = []
        for col in stmt.columns[:4]:  # Last 4 periods
            period_data = {}
            for row in stmt.index:
                value = stmt.loc[row, col]
                if hasattr(value, 'item'):
                    value = value.item()
                period_data[str(row)] = value
            
            periods.append({
                "period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col),
                "data": period_data
            })
        
        return {
            "type": "quarterly" if quarterly else "annual",
            "periods": periods
        }
    
    def get_cash_flow(self, symbol: str, quarterly: bool = False) -> Dict[str, Any]:
        """
        Get cash flow statement data.
        
        Returns: operating, investing, financing cash flows for recent periods
        """
        ticker = self._get_ticker(symbol)
        
        if quarterly:
            stmt = ticker.quarterly_cashflow
        else:
            stmt = ticker.cashflow
        
        if stmt is None or stmt.empty:
            return {"periods": [], "error": "No cash flow data available"}
        
        periods = []
        for col in stmt.columns[:4]:  # Last 4 periods
            period_data = {}
            for row in stmt.index:
                value = stmt.loc[row, col]
                if hasattr(value, 'item'):
                    value = value.item()
                period_data[str(row)] = value
            
            periods.append({
                "period": col.strftime("%Y-%m-%d") if hasattr(col, 'strftime') else str(col),
                "data": period_data
            })
        
        return {
            "type": "quarterly" if quarterly else "annual",
            "periods": periods
        }
    
    # ==========================================
    # Earnings & Analyst Data
    # ==========================================
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """
        Get earnings history and estimates.
        
        Returns: historical EPS, earnings dates, surprise %
        """
        ticker = self._get_ticker(symbol)
        
        result = {
            "earnings_history": [],
            "next_earnings_date": None
        }
        
        # Earnings history
        try:
            earnings = ticker.earnings_history
            if earnings is not None and not earnings.empty:
                for _, row in earnings.iterrows():
                    result["earnings_history"].append({
                        "period": str(row.get("period", "")),
                        "eps_estimate": row.get("epsEstimate"),
                        "eps_actual": row.get("epsActual"),
                        "surprise_pct": row.get("surprisePercent"),
                    })
        except Exception:
            pass
        
        # Next earnings date
        try:
            calendar = ticker.calendar
            if calendar is not None:
                if isinstance(calendar, dict):
                    earnings_date = calendar.get("Earnings Date")
                    if earnings_date:
                        result["next_earnings_date"] = str(earnings_date[0]) if isinstance(earnings_date, list) else str(earnings_date)
        except Exception:
            pass
        
        return result
    
    def get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """
        Get analyst recommendations and price targets.
        
        Returns: recommendation counts, price targets
        """
        ticker = self._get_ticker(symbol)
        info = ticker.info
        
        result = {
            "target_high": info.get("targetHighPrice"),
            "target_low": info.get("targetLowPrice"),
            "target_mean": info.get("targetMeanPrice"),
            "target_median": info.get("targetMedianPrice"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "recommendation": info.get("recommendationKey", "none"),
            "recommendation_mean": info.get("recommendationMean"),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
        }
        
        # Calculate upside/downside potential
        if result["current_price"] and result["target_mean"]:
            result["upside_potential_pct"] = round(
                ((result["target_mean"] - result["current_price"]) / result["current_price"]) * 100, 2
            )
        else:
            result["upside_potential_pct"] = None
        
        return result
    
    # ==========================================
    # Historical Price Data
    # ==========================================
    
    def get_price_history(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """
        Get historical price data.
        
        Args:
            symbol: Stock ticker
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo)
        
        Returns: OHLCV data with summary statistics
        """
        ticker = self._get_ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist is None or hist.empty:
            return {"error": "No price history available"}
        
        # Current price info
        latest = hist.iloc[-1]
        first = hist.iloc[0]
        
        return {
            "period": period,
            "interval": interval,
            "data_points": len(hist),
            "latest_close": round(float(latest["Close"]), 2),
            "period_open": round(float(first["Open"]), 2),
            "period_high": round(float(hist["High"].max()), 2),
            "period_low": round(float(hist["Low"].min()), 2),
            "period_return_pct": round(((float(latest["Close"]) - float(first["Open"])) / float(first["Open"])) * 100, 2),
            "avg_volume": int(hist["Volume"].mean()),
            "latest_volume": int(latest["Volume"]),
            # 52-week data
            "high_52w": round(float(hist["High"].tail(252).max()), 2) if len(hist) >= 252 else round(float(hist["High"].max()), 2),
            "low_52w": round(float(hist["Low"].tail(252).min()), 2) if len(hist) >= 252 else round(float(hist["Low"].min()), 2),
        }
    
    # ==========================================
    # Dividends & Splits
    # ==========================================
    
    def get_dividends(self, symbol: str) -> Dict[str, Any]:
        """
        Get dividend history.
        
        Returns: recent dividends, yield, frequency
        """
        ticker = self._get_ticker(symbol)
        dividends = ticker.dividends
        
        if dividends is None or dividends.empty:
            return {
                "has_dividends": False,
                "recent_dividends": [],
                "annual_dividend": None,
                "dividend_yield": None
            }
        
        # Last 8 dividends
        recent = dividends.tail(8)
        recent_list = [
            {
                "date": idx.strftime("%Y-%m-%d"),
                "amount": round(float(val), 4)
            }
            for idx, val in recent.items()
        ]
        
        info = ticker.info
        
        return {
            "has_dividends": True,
            "recent_dividends": recent_list,
            "annual_dividend": info.get("dividendRate"),
            "dividend_yield": info.get("dividendYield"),
            "ex_dividend_date": info.get("exDividendDate"),
            "payout_ratio": info.get("payoutRatio"),
        }
    
    def clear_cache(self):
        """Clear the ticker cache"""
        self._cache = {}


# Global instance for reuse across agents
yfinance_tool = YFinanceTool()