"""
Central import point for all intent tasks

This file enables Celery's autodiscover_tasks() to find all tasks.
Just import new task functions here as you add intents.
"""

# Import task functions from intent modules
from .analyze_stock import analyze_stock_task

# When you add more intents, add them here:
# from .compare_stocks import compare_stocks_task
# from .market_scan import market_scan_task
# from .news_impact import news_impact_task

__all__ = [
    'analyze_stock_task',
    # 'compare_stocks_task',
    # 'market_scan_task',
]