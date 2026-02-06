"""
Fundamentals Agent - Analyzes financial health and valuation of a stock

Gathers and analyzes:
- Key financial ratios (P/E, P/B, ROE, etc.)
- Income statement trends (revenue, earnings growth)
- Balance sheet health (debt levels, liquidity)
- Cash flow analysis
- Dividend information
- Analyst estimates and price targets

Uses yfinance as the primary data source.
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from ..tools.yfinance_tool import yfinance_tool


class FundamentalAgent(BaseAgent):
    """
    Agent that performs fundamental analysis on a stock.
    
    Inherits from BaseAgent which provides:
    - run() with retry logic and timing
    - Standardized result format
    - Parameter validation
    """
    
    def __init__(self):
        super().__init__(
            name="fundamental_agent",
            description="Analyzes financial health, valuation ratios, and growth metrics"
        )
        self.tool = yfinance_tool
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform fundamental analysis on a stock.
        
        Called by BaseAgent.run() which wraps this in retry logic.
        
        Args:
            parameters: {"symbol": "AAPL", "analysis_depth": "deep"|"quick"}
        
        Returns:
            Dict with complete fundamental analysis
        """
        # Validate we have a symbol
        self.validate_parameters(parameters, ["symbol"])
        symbol = parameters["symbol"].upper()
        depth = parameters.get("analysis_depth", "deep")
        
        print(f"      📊 Fetching fundamental data for {symbol}...")
        
        # ---- Gather data from yfinance tool ----
        
        # Always fetch these (quick + deep)
        company_info = self.tool.get_company_info(symbol)
        key_ratios = self.tool.get_key_ratios(symbol)
        price_data = self.tool.get_price_history(symbol, period="1y")
        analyst_data = self.tool.get_analyst_recommendations(symbol)
        
        # Deep analysis fetches additional data
        income_data = None
        balance_data = None
        cashflow_data = None
        dividend_data = None
        earnings_data = None
        
        if depth == "deep":
            print(f"      📊 Running deep analysis for {symbol}...")
            income_data = self.tool.get_income_statement(symbol)
            balance_data = self.tool.get_balance_sheet(symbol)
            cashflow_data = self.tool.get_cash_flow(symbol)
            dividend_data = self.tool.get_dividends(symbol)
            earnings_data = self.tool.get_earnings(symbol)
        
        # ---- Compute scores and assessment ----
        
        valuation_score = self._score_valuation(key_ratios)
        profitability_score = self._score_profitability(key_ratios)
        growth_score = self._score_growth(key_ratios)
        financial_health_score = self._score_financial_health(key_ratios)
        
        # Overall fundamental score (weighted average)
        overall_score = round(
            valuation_score * 0.25 +
            profitability_score * 0.25 +
            growth_score * 0.25 +
            financial_health_score * 0.25,
            1
        )
        
        # ---- Build result ----
        
        result = {
            "symbol": symbol,
            "company": {
                "name": company_info.get("name"),
                "sector": company_info.get("sector"),
                "industry": company_info.get("industry"),
                "market_cap": company_info.get("market_cap"),
                "employees": company_info.get("employees"),
            },
            "valuation": {
                "pe_trailing": key_ratios.get("pe_trailing"),
                "pe_forward": key_ratios.get("pe_forward"),
                "peg_ratio": key_ratios.get("peg_ratio"),
                "price_to_book": key_ratios.get("price_to_book"),
                "price_to_sales": key_ratios.get("price_to_sales"),
                "ev_to_ebitda": key_ratios.get("ev_to_ebitda"),
                "score": valuation_score,
            },
            "profitability": {
                "gross_margin": key_ratios.get("gross_margin"),
                "operating_margin": key_ratios.get("operating_margin"),
                "profit_margin": key_ratios.get("profit_margin"),
                "roe": key_ratios.get("roe"),
                "roa": key_ratios.get("roa"),
                "score": profitability_score,
            },
            "growth": {
                "revenue_growth": key_ratios.get("revenue_growth"),
                "earnings_growth": key_ratios.get("earnings_growth"),
                "score": growth_score,
            },
            "financial_health": {
                "current_ratio": key_ratios.get("current_ratio"),
                "debt_to_equity": key_ratios.get("debt_to_equity"),
                "quick_ratio": key_ratios.get("quick_ratio"),
                "score": financial_health_score,
            },
            "price_context": {
                "current_price": price_data.get("latest_close"),
                "52w_high": price_data.get("high_52w"),
                "52w_low": price_data.get("low_52w"),
                "ytd_return_pct": price_data.get("period_return_pct"),
            },
            "analyst": analyst_data,
            "scores": {
                "valuation": valuation_score,
                "profitability": profitability_score,
                "growth": growth_score,
                "financial_health": financial_health_score,
                "overall": overall_score,
            },
            "assessment": self._generate_assessment(
                overall_score, valuation_score, profitability_score,
                growth_score, financial_health_score, key_ratios
            ),
        }
        
        # Add deep analysis data if available
        if depth == "deep":
            result["income_statement"] = income_data
            result["balance_sheet"] = balance_data
            result["cash_flow"] = cashflow_data
            result["dividends"] = dividend_data
            result["earnings"] = earnings_data
        
        return result
    
    # ==========================================
    # Scoring Methods (each returns 0-10)
    # ==========================================
    
    def _score_valuation(self, ratios: Dict) -> float:
        """
        Score valuation metrics (0-10).
        Lower P/E, P/B = higher score (more undervalued)
        """
        score = 5.0  # Start neutral
        
        pe = ratios.get("pe_trailing")
        if pe is not None:
            if pe < 0:
                score -= 2.0       # Negative earnings
            elif pe < 10:
                score += 2.5       # Very cheap
            elif pe < 15:
                score += 1.5       # Reasonably valued
            elif pe < 25:
                score += 0.0       # Fairly valued
            elif pe < 40:
                score -= 1.0       # Expensive
            else:
                score -= 2.0       # Very expensive
        
        peg = ratios.get("peg_ratio")
        if peg is not None:
            if 0 < peg < 1:
                score += 1.5       # Undervalued relative to growth
            elif 1 <= peg < 2:
                score += 0.5       # Fair
            elif peg >= 2:
                score -= 1.0       # Overvalued relative to growth
        
        pb = ratios.get("price_to_book")
        if pb is not None:
            if 0 < pb < 1:
                score += 1.0       # Trading below book value
            elif pb < 3:
                score += 0.5       # Reasonable
            elif pb > 10:
                score -= 1.0       # Very expensive
        
        return round(max(0, min(10, score)), 1)
    
    def _score_profitability(self, ratios: Dict) -> float:
        """
        Score profitability metrics (0-10).
        Higher margins and returns = higher score
        """
        score = 5.0
        
        profit_margin = ratios.get("profit_margin")
        if profit_margin is not None:
            if profit_margin > 0.20:
                score += 2.0       # Excellent margins
            elif profit_margin > 0.10:
                score += 1.0       # Good margins
            elif profit_margin > 0:
                score += 0.0       # Profitable but thin
            else:
                score -= 2.0       # Unprofitable
        
        roe = ratios.get("roe")
        if roe is not None:
            if roe > 0.20:
                score += 2.0       # Excellent return on equity
            elif roe > 0.10:
                score += 1.0       # Good
            elif roe > 0:
                score += 0.0       # Positive but low
            else:
                score -= 1.5       # Negative ROE
        
        operating_margin = ratios.get("operating_margin")
        if operating_margin is not None:
            if operating_margin > 0.25:
                score += 1.0       # Strong operating efficiency
            elif operating_margin < 0:
                score -= 1.0       # Operating losses
        
        return round(max(0, min(10, score)), 1)
    
    def _score_growth(self, ratios: Dict) -> float:
        """
        Score growth metrics (0-10).
        Higher growth = higher score
        """
        score = 5.0
        
        rev_growth = ratios.get("revenue_growth")
        if rev_growth is not None:
            if rev_growth > 0.25:
                score += 2.5       # Hyper growth
            elif rev_growth > 0.10:
                score += 1.5       # Strong growth
            elif rev_growth > 0:
                score += 0.5       # Moderate growth
            else:
                score -= 1.5       # Declining revenue
        
        earn_growth = ratios.get("earnings_growth")
        if earn_growth is not None:
            if earn_growth > 0.25:
                score += 2.0       # Strong earnings growth
            elif earn_growth > 0.10:
                score += 1.0       # Good
            elif earn_growth > 0:
                score += 0.0       # Moderate
            else:
                score -= 1.5       # Declining earnings
        
        return round(max(0, min(10, score)), 1)
    
    def _score_financial_health(self, ratios: Dict) -> float:
        """
        Score financial health / balance sheet strength (0-10).
        Lower debt, higher liquidity = higher score
        """
        score = 5.0
        
        current_ratio = ratios.get("current_ratio")
        if current_ratio is not None:
            if current_ratio > 2.0:
                score += 2.0       # Very liquid
            elif current_ratio > 1.5:
                score += 1.0       # Healthy
            elif current_ratio > 1.0:
                score += 0.0       # Adequate
            else:
                score -= 2.0       # Liquidity risk
        
        dte = ratios.get("debt_to_equity")
        if dte is not None:
            if dte < 0.3:
                score += 2.0       # Very low debt
            elif dte < 0.5:
                score += 1.5       # Conservative
            elif dte < 1.0:
                score += 0.5       # Moderate debt
            elif dte < 2.0:
                score -= 0.5       # High debt
            else:
                score -= 2.0       # Very high debt
        
        quick = ratios.get("quick_ratio")
        if quick is not None:
            if quick > 1.5:
                score += 1.0       # Strong short-term liquidity
            elif quick < 0.5:
                score -= 1.0       # Short-term liquidity risk
        
        return round(max(0, min(10, score)), 1)
    
    # ==========================================
    # Assessment Generation
    # ==========================================
    
    def _generate_assessment(self, overall: float, valuation: float,
                            profitability: float, growth: float,
                            health: float, ratios: Dict) -> Dict[str, Any]:
        """
        Generate a human-readable assessment based on scores.
        """
        # Overall rating
        if overall >= 8:
            rating = "STRONG_BUY"
            summary = "Fundamentals are excellent across all metrics."
        elif overall >= 6.5:
            rating = "BUY"
            summary = "Fundamentals are solid with minor concerns."
        elif overall >= 5:
            rating = "HOLD"
            summary = "Fundamentals are mixed — some strengths offset by weaknesses."
        elif overall >= 3.5:
            rating = "SELL"
            summary = "Fundamentals show significant concerns."
        else:
            rating = "STRONG_SELL"
            summary = "Fundamentals are weak across most metrics."
        
        # Identify strengths and weaknesses
        categories = {
            "Valuation": valuation,
            "Profitability": profitability,
            "Growth": growth,
            "Financial Health": health,
        }
        
        strengths = [name for name, score in categories.items() if score >= 7.0]
        weaknesses = [name for name, score in categories.items() if score < 4.0]
        
        return {
            "rating": rating,
            "overall_score": overall,
            "summary": summary,
            "strengths": strengths if strengths else ["No standout strengths identified"],
            "weaknesses": weaknesses if weaknesses else ["No major weaknesses identified"],
        }