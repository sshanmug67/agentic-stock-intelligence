from typing import Dict, Type
from .base_intent import BaseIntent
from .analyze_stock import AnalyzeStockIntent
from .compare_stocks import CompareStocksIntent

class IntentRegistry:
    """Central registry of all intents"""
    
    _intents: Dict[str, Type[BaseIntent]] = {}
    
    @classmethod
    def register(cls, intent_type: str, intent_class: Type[BaseIntent]):
        """Register an intent"""
        cls._intents[intent_type] = intent_class
    
    @classmethod
    def get(cls, intent_type: str) -> Type[BaseIntent]:
        """Get intent class by type"""
        if intent_type not in cls._intents:
            raise ValueError(f"Unknown intent type: {intent_type}")
        return cls._intents[intent_type]
    
    @classmethod
    def list_intents(cls) -> list[str]:
        """List all registered intents"""
        return list(cls._intents.keys())

# Auto-register intents
IntentRegistry.register("analyze_stock", AnalyzeStockIntent)
IntentRegistry.register("compare_stocks", CompareStocksIntent)