"""
Configuration management for Stock Intelligence Pipeline

Approach (same pattern as CVE system):
- Single app_config.yaml for structure and safe defaults (committed as example)
- All environment-specific config via environment variables
- No secrets in config files
- Priority: Environment Variables > .env > YAML > Hardcoded Defaults
"""
import os
import yaml
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings:
    """Application configuration for Stock Intelligence Pipeline"""
    
    def __init__(self):
        """Initialize with hardcoded defaults"""
        
        # =============================================================
        # Application
        # =============================================================
        self.app_name: str = "Stock Intelligence Pipeline"
        self.environment: str = "development"
        self.debug: bool = True
        self.log_level: str = "INFO"
        
        # =============================================================
        # API Server
        # =============================================================
        self.api_host: str = "0.0.0.0"
        self.api_port: int = 8000
        self.api_prefix: str = "/api/v1"
        
        # =============================================================
        # CORS
        # =============================================================
        self.cors_origins: list[str] = [
            "http://localhost:3000",
            "http://localhost:5173"
        ]
        
        # =============================================================
        # Redis
        # =============================================================
        self.redis_host: str = "localhost"
        self.redis_port: int = 6379
        self.redis_db: int = 0
        self.redis_password: Optional[str] = None
        
        # =============================================================
        # Celery
        # =============================================================
        self.celery_broker_url: Optional[str] = None
        self.celery_result_backend: Optional[str] = None
        
        # =============================================================
        # Supabase
        # =============================================================
        self.supabase_url: Optional[str] = None
        self.supabase_key: Optional[str] = None
        self.supabase_service_key: Optional[str] = None
        
        # =============================================================
        # LLM
        # =============================================================
        self.openai_api_key: Optional[str] = None
        self.llm_model: str = "GPT-4o-mini"
        
        # =============================================================
        # Stock Data APIs
        # =============================================================
        self.alpha_vantage_key: Optional[str] = None
        self.finnhub_key: Optional[str] = None
        self.twelve_data_key: Optional[str] = None
        self.fmp_key: Optional[str] = None  # Financial Modeling Prep
        
        # =============================================================
        # YFinance Settings (no key needed)
        # =============================================================
        self.yfinance_enabled: bool = True
        self.yfinance_cache_ttl: int = 300          # 5 minutes
        self.yfinance_request_timeout: int = 30      # seconds
        
        # =============================================================
        # Agent Settings
        # =============================================================
        # Fundamental Agent
        self.fundamental_agent_enabled: bool = True
        self.fundamental_agent_default_depth: str = "deep"  # "quick" or "deep"
        
        # Technical Agent
        self.technical_agent_enabled: bool = True
        self.technical_agent_price_period: str = "1y"
        self.technical_agent_price_interval: str = "1d"
        
        # News & Sentiment Agent
        self.news_agent_enabled: bool = True
        self.news_agent_lookback_days: int = 30
        self.news_agent_max_articles: int = 50
        
        # Aggregation Agent
        self.aggregation_agent_enabled: bool = True
        self.aggregation_agent_use_llm: bool = False  # Start without LLM
        
        # =============================================================
        # Execution Settings
        # =============================================================
        self.execution_ttl_seconds: int = 86400     # 24 hours in Redis
        self.execution_max_concurrent: int = 10
        self.execution_task_timeout: int = 3600     # 1 hour max per task
        self.execution_soft_timeout: int = 3000     # 50 min soft limit
        
        logger.info("✅ Settings: Initialized with defaults")
    
    # =================================================================
    # LOAD (Entry Point)
    # =================================================================
    
    @classmethod
    def load(cls, config_file: str = None) -> "Settings":
        """
        Load configuration with priority order:
        
        1. Environment Variables (HIGHEST PRIORITY)
        2. .env file
        3. app_config.yaml (structure and safe defaults)
        4. Hardcoded defaults (fallback)
        
        Args:
            config_file: Path to YAML config file. 
                         Defaults to stock_intelligence_pipeline/config/app_config.yaml
        
        Returns:
            Settings instance
        """
        settings = cls()
        
        # Step 1: Load .env file if it exists
        settings._load_dotenv()
        
        # Step 2: Load defaults from YAML
        if config_file is None:
            config_file = str(settings._get_project_root() / "config" / "app_config.yaml")
        settings._load_from_yaml(config_file)
        
        # Step 3: Override with environment variables (highest priority)
        settings._load_from_environment()
        
        # Step 4: Validate
        if not settings.validate():
            logger.warning("⚠️  Configuration has validation warnings (non-fatal)")
        
        return settings
    
    # =================================================================
    # Path Helpers
    # =================================================================
    
    def _get_project_root(self) -> Path:
        """
        Get project root directory.
        
        This file: stock_intelligence_pipeline/backend/config/settings.py
        Root is 2 levels up: config/ -> backend/ -> stock_intelligence_pipeline/
        """
        return Path(__file__).resolve().parent.parent.parent
    
    # =================================================================
    # Step 1: Load .env
    # =================================================================
    
    def _load_dotenv(self):
        """Load .env file if it exists (for local development)"""
        env_file = self._get_project_root() / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                logger.info("✅ Settings: Loaded .env file")
            except ImportError:
                logger.warning("⚠️  python-dotenv not installed, skipping .env")
    
    # =================================================================
    # Step 2: Load from YAML
    # =================================================================
    
    def _load_from_yaml(self, filepath: str):
        """Load configuration from YAML file"""
        config_file = Path(filepath)
        
        if not config_file.exists():
            logger.warning(f"⚠️  Config file not found: {filepath}")
            logger.info("   Copy app_config.example.yaml to app_config.yaml")
            logger.info("   Using hardcoded defaults")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning(f"⚠️  Config file is empty: {filepath}")
                return
            
            # --- Application ---
            if "app" in data:
                app = data["app"]
                self.app_name = app.get("name", self.app_name)
                self.environment = app.get("environment", self.environment)
                self.debug = app.get("debug", self.debug)
                self.log_level = app.get("log_level", self.log_level)
            
            # --- API Server ---
            if "api" in data:
                api = data["api"]
                self.api_host = api.get("host", self.api_host)
                self.api_port = api.get("port", self.api_port)
                self.api_prefix = api.get("prefix", self.api_prefix)
            
            # --- CORS ---
            if "cors" in data:
                cors = data["cors"]
                self.cors_origins = cors.get("origins", self.cors_origins)
            
            # --- Redis ---
            if "redis" in data:
                redis = data["redis"]
                self.redis_host = redis.get("host", self.redis_host)
                self.redis_port = redis.get("port", self.redis_port)
                self.redis_db = redis.get("db", self.redis_db)
                self.redis_password = redis.get("password", self.redis_password)
            
            # --- Celery ---
            if "celery" in data:
                celery = data["celery"]
                self.celery_broker_url = celery.get("broker_url", self.celery_broker_url)
                self.celery_result_backend = celery.get("result_backend", self.celery_result_backend)
            
            # --- Supabase ---
            if "supabase" in data:
                supabase = data["supabase"]
                self.supabase_url = supabase.get("url", self.supabase_url)
                self.supabase_key = supabase.get("key", self.supabase_key)
                self.supabase_service_key = supabase.get("service_key", self.supabase_service_key)
            
            # --- LLM ---
            if "llm" in data:
                llm = data["llm"]
                self.openai_api_key = llm.get("openai_api_key", self.openai_api_key)
                self.llm_model = llm.get("model", self.llm_model)
            
            # --- Stock APIs ---
            if "stock_apis" in data:
                apis = data["stock_apis"]
                self.alpha_vantage_key = apis.get("alpha_vantage_key", self.alpha_vantage_key)
                self.finnhub_key = apis.get("finnhub_key", self.finnhub_key)
                self.twelve_data_key = apis.get("twelve_data_key", self.twelve_data_key)
                self.fmp_key = apis.get("fmp_key", self.fmp_key)
            
            # --- YFinance ---
            if "yfinance" in data:
                yf = data["yfinance"]
                self.yfinance_enabled = yf.get("enabled", self.yfinance_enabled)
                self.yfinance_cache_ttl = yf.get("cache_ttl", self.yfinance_cache_ttl)
                self.yfinance_request_timeout = yf.get("request_timeout", self.yfinance_request_timeout)
            
            # --- Agents ---
            if "agents" in data:
                agents = data["agents"]
                
                if "fundamental" in agents:
                    fundamental = agents["fundamental"]
                    self.fundamental_agent_enabled = fundamental.get("enabled", self.fundamental_agent_enabled)
                    self.fundamental_agent_default_depth = fundamental.get("default_depth", self.fundamental_agent_default_depth)
                
                if "technical" in agents:
                    technical = agents["technical"]
                    self.technical_agent_enabled = technical.get("enabled", self.technical_agent_enabled)
                    self.technical_agent_price_period = technical.get("price_period", self.technical_agent_price_period)
                    self.technical_agent_price_interval = technical.get("price_interval", self.technical_agent_price_interval)
                
                if "news" in agents:
                    news = agents["news"]
                    self.news_agent_enabled = news.get("enabled", self.news_agent_enabled)
                    self.news_agent_lookback_days = news.get("lookback_days", self.news_agent_lookback_days)
                    self.news_agent_max_articles = news.get("max_articles", self.news_agent_max_articles)
                
                if "aggregation" in agents:
                    aggregation = agents["aggregation"]
                    self.aggregation_agent_enabled = aggregation.get("enabled", self.aggregation_agent_enabled)
                    self.aggregation_agent_use_llm = aggregation.get("use_llm", self.aggregation_agent_use_llm)
            
            # --- Execution ---
            if "execution" in data:
                execution = data["execution"]
                self.execution_ttl_seconds = execution.get("ttl_seconds", self.execution_ttl_seconds)
                self.execution_max_concurrent = execution.get("max_concurrent", self.execution_max_concurrent)
                self.execution_task_timeout = execution.get("task_timeout", self.execution_task_timeout)
                self.execution_soft_timeout = execution.get("soft_timeout", self.execution_soft_timeout)
            
            logger.info(f"✅ Settings: Loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error loading YAML config: {e}")
            logger.info("   Using hardcoded defaults")
    
    # =================================================================
    # Step 3: Load from Environment Variables
    # =================================================================
    
    def _load_from_environment(self):
        """Load configuration from environment variables (highest priority)"""
        
        # --- Application ---
        if os.getenv("ENVIRONMENT"):
            self.environment = os.getenv("ENVIRONMENT")
            logger.info(f"✓ ENVIRONMENT: {self.environment}")
        
        if os.getenv("DEBUG"):
            self.debug = os.getenv("DEBUG").lower() == "true"
            logger.info(f"✓ DEBUG: {self.debug}")
        
        if os.getenv("LOG_LEVEL"):
            self.log_level = os.getenv("LOG_LEVEL")
            logger.info(f"✓ LOG_LEVEL: {self.log_level}")
        
        # --- API Server ---
        if os.getenv("API_HOST"):
            self.api_host = os.getenv("API_HOST")
            logger.info(f"✓ API_HOST: {self.api_host}")
        
        if os.getenv("API_PORT"):
            self.api_port = int(os.getenv("API_PORT"))
            logger.info(f"✓ API_PORT: {self.api_port}")
        
        # --- Redis ---
        if os.getenv("REDIS_HOST"):
            self.redis_host = os.getenv("REDIS_HOST")
            logger.info(f"✓ REDIS_HOST: {self.redis_host}")
        
        if os.getenv("REDIS_PORT"):
            self.redis_port = int(os.getenv("REDIS_PORT"))
            logger.info(f"✓ REDIS_PORT: {self.redis_port}")
        
        if os.getenv("REDIS_DB"):
            self.redis_db = int(os.getenv("REDIS_DB"))
            logger.info(f"✓ REDIS_DB: {self.redis_db}")
        
        if os.getenv("REDIS_PASSWORD"):
            self.redis_password = os.getenv("REDIS_PASSWORD")
            logger.info("✓ REDIS_PASSWORD: Set")
        
        # --- Celery ---
        if os.getenv("CELERY_BROKER_URL"):
            self.celery_broker_url = os.getenv("CELERY_BROKER_URL")
            logger.info("✓ CELERY_BROKER_URL: Set")
        
        if os.getenv("CELERY_RESULT_BACKEND"):
            self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
            logger.info("✓ CELERY_RESULT_BACKEND: Set")
        
        # --- Supabase ---
        if os.getenv("SUPABASE_URL"):
            self.supabase_url = os.getenv("SUPABASE_URL")
            logger.info("✓ SUPABASE_URL: Set")
        
        if os.getenv("SUPABASE_KEY"):
            self.supabase_key = os.getenv("SUPABASE_KEY")
            logger.info("✓ SUPABASE_KEY: Set")
        
        if os.getenv("SUPABASE_SERVICE_KEY"):
            self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
            logger.info("✓ SUPABASE_SERVICE_KEY: Set")
        
        # --- LLM ---
        if os.getenv("OPENAI_API_KEY"):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            logger.info("✓ OPENAI_API_KEY: Set")
        
        if os.getenv("LLM_MODEL"):
            self.llm_model = os.getenv("LLM_MODEL")
            logger.info(f"✓ LLM_MODEL: {self.llm_model}")
        
        # --- Stock APIs ---
        if os.getenv("ALPHA_VANTAGE_KEY"):
            self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
            logger.info("✓ ALPHA_VANTAGE_KEY: Set")
        
        if os.getenv("FINNHUB_KEY"):
            self.finnhub_key = os.getenv("FINNHUB_KEY")
            logger.info("✓ FINNHUB_KEY: Set")
        
        if os.getenv("TWELVE_DATA_KEY"):
            self.twelve_data_key = os.getenv("TWELVE_DATA_KEY")
            logger.info("✓ TWELVE_DATA_KEY: Set")
        
        if os.getenv("FMP_KEY"):
            self.fmp_key = os.getenv("FMP_KEY")
            logger.info("✓ FMP_KEY: Set")
        
        # --- Agent Toggles ---
        if os.getenv("FUNDAMENTAL_AGENT_ENABLED"):
            self.fundamental_agent_enabled = os.getenv("FUNDAMENTAL_AGENT_ENABLED").lower() == "true"
            logger.info(f"✓ FUNDAMENTAL_AGENT_ENABLED: {self.fundamental_agent_enabled}")
        
        if os.getenv("TECHNICAL_AGENT_ENABLED"):
            self.technical_agent_enabled = os.getenv("TECHNICAL_AGENT_ENABLED").lower() == "true"
            logger.info(f"✓ TECHNICAL_AGENT_ENABLED: {self.technical_agent_enabled}")
        
        if os.getenv("NEWS_AGENT_ENABLED"):
            self.news_agent_enabled = os.getenv("NEWS_AGENT_ENABLED").lower() == "true"
            logger.info(f"✓ NEWS_AGENT_ENABLED: {self.news_agent_enabled}")
        
        if os.getenv("AGGREGATION_AGENT_ENABLED"):
            self.aggregation_agent_enabled = os.getenv("AGGREGATION_AGENT_ENABLED").lower() == "true"
            logger.info(f"✓ AGGREGATION_AGENT_ENABLED: {self.aggregation_agent_enabled}")
        
        # --- Execution ---
        if os.getenv("EXECUTION_TTL_SECONDS"):
            self.execution_ttl_seconds = int(os.getenv("EXECUTION_TTL_SECONDS"))
            logger.info(f"✓ EXECUTION_TTL_SECONDS: {self.execution_ttl_seconds}")
        
        if os.getenv("EXECUTION_MAX_CONCURRENT"):
            self.execution_max_concurrent = int(os.getenv("EXECUTION_MAX_CONCURRENT"))
            logger.info(f"✓ EXECUTION_MAX_CONCURRENT: {self.execution_max_concurrent}")
        
        logger.info("✅ Settings: Loaded environment overrides")
    
    # =================================================================
    # Validation
    # =================================================================
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        warnings = []
        
        # --- API Keys (warnings, not errors - yfinance works without them) ---
        if not self.openai_api_key:
            warnings.append("OPENAI_API_KEY not set - LLM features will be disabled")
        
        if not self.alpha_vantage_key:
            warnings.append("ALPHA_VANTAGE_KEY not set - using yfinance as fallback")
        
        if not self.finnhub_key:
            warnings.append("FINNHUB_KEY not set - news agent will use alternative sources")
        
        # --- Redis (required for Celery) ---
        if not self.redis_host:
            errors.append("REDIS_HOST cannot be empty")
        
        if self.redis_port < 1 or self.redis_port > 65535:
            errors.append("REDIS_PORT must be between 1 and 65535")
        
        # --- API Server ---
        if self.api_port < 1 or self.api_port > 65535:
            errors.append("API_PORT must be between 1 and 65535")
        
        # --- Execution ---
        if self.execution_ttl_seconds < 60:
            errors.append("EXECUTION_TTL_SECONDS must be at least 60")
        
        if self.execution_task_timeout < 60:
            errors.append("EXECUTION_TASK_TIMEOUT must be at least 60")
        
        if self.execution_soft_timeout >= self.execution_task_timeout:
            errors.append("EXECUTION_SOFT_TIMEOUT must be less than EXECUTION_TASK_TIMEOUT")
        
        if self.execution_max_concurrent < 1:
            errors.append("EXECUTION_MAX_CONCURRENT must be at least 1")
        
        # --- YFinance ---
        if self.yfinance_cache_ttl < 0:
            errors.append("YFINANCE_CACHE_TTL cannot be negative")
        
        if self.yfinance_request_timeout < 5:
            errors.append("YFINANCE_REQUEST_TIMEOUT must be at least 5 seconds")
        
        # --- Agent Settings ---
        if self.fundamental_agent_default_depth not in ["quick", "deep"]:
            errors.append("FUNDAMENTAL_AGENT_DEFAULT_DEPTH must be 'quick' or 'deep'")
        
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
        if self.technical_agent_price_period not in valid_periods:
            errors.append(f"TECHNICAL_AGENT_PRICE_PERIOD must be one of: {valid_periods}")
        
        if self.news_agent_lookback_days < 1 or self.news_agent_lookback_days > 365:
            errors.append("NEWS_AGENT_LOOKBACK_DAYS must be between 1 and 365")
        
        if self.news_agent_max_articles < 1 or self.news_agent_max_articles > 500:
            errors.append("NEWS_AGENT_MAX_ARTICLES must be between 1 and 500")
        
        # --- Log results ---
        if warnings:
            logger.warning("\n⚠️  Configuration Warnings:")
            for warning in warnings:
                logger.warning(f"   - {warning}")
        
        if errors:
            logger.error("\n❌ Configuration Errors:")
            for error in errors:
                logger.error(f"   - {error}")
            return False
        
        logger.info("✅ Settings: Validation passed")
        return True
    
    # =================================================================
    # Computed Properties
    # =================================================================
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def celery_broker(self) -> str:
        """Get Celery broker URL (defaults to Redis)"""
        return self.celery_broker_url or self.redis_url
    
    @property
    def celery_backend(self) -> str:
        """Get Celery result backend URL (defaults to Redis)"""
        return self.celery_result_backend or self.redis_url
    
    # =================================================================
    # Print Summary
    # =================================================================
    
    def print_summary(self):
        """Print configuration summary"""
        # Import here to avoid circular imports
        from ..utils.logging_config import log_info_raw
        
        log_info_raw("\n" + "=" * 70)
        log_info_raw("STOCK INTELLIGENCE PIPELINE - CONFIGURATION SUMMARY")
        log_info_raw("=" * 70)
        
        log_info_raw(f"\nApplication:")
        log_info_raw(f"  - Name: {self.app_name}")
        log_info_raw(f"  - Environment: {self.environment}")
        log_info_raw(f"  - Debug: {'✅ On' if self.debug else '❌ Off'}")
        log_info_raw(f"  - Log Level: {self.log_level}")
        
        log_info_raw(f"\nAPI Server:")
        log_info_raw(f"  - Host: {self.api_host}")
        log_info_raw(f"  - Port: {self.api_port}")
        log_info_raw(f"  - Prefix: {self.api_prefix}")
        log_info_raw(f"  - CORS Origins: {self.cors_origins}")
        
        log_info_raw(f"\nRedis:")
        log_info_raw(f"  - Host: {self.redis_host}")
        log_info_raw(f"  - Port: {self.redis_port}")
        log_info_raw(f"  - DB: {self.redis_db}")
        log_info_raw(f"  - Password: {'✅ Set' if self.redis_password else '❌ Not set'}")
        log_info_raw(f"  - URL: {self.redis_url}")
        
        log_info_raw(f"\nCelery:")
        log_info_raw(f"  - Broker: {self.celery_broker}")
        log_info_raw(f"  - Result Backend: {self.celery_backend}")
        
        log_info_raw(f"\nAPI Keys:")
        log_info_raw(f"  - OpenAI: {'✅ Set' if self.openai_api_key else '⚠️  Not set (LLM disabled)'}")
        log_info_raw(f"  - Alpha Vantage: {'✅ Set' if self.alpha_vantage_key else '⚠️  Not set'}")
        log_info_raw(f"  - Finnhub: {'✅ Set' if self.finnhub_key else '⚠️  Not set'}")
        log_info_raw(f"  - Twelve Data: {'✅ Set' if self.twelve_data_key else '⚠️  Not set'}")
        log_info_raw(f"  - Financial Modeling Prep: {'✅ Set' if self.fmp_key else '⚠️  Not set'}")
        
        log_info_raw(f"\nSupabase:")
        log_info_raw(f"  - URL: {'✅ Set' if self.supabase_url else '⚠️  Not set'}")
        log_info_raw(f"  - Key: {'✅ Set' if self.supabase_key else '⚠️  Not set'}")
        log_info_raw(f"  - Service Key: {'✅ Set' if self.supabase_service_key else '⚠️  Not set'}")
        
        log_info_raw(f"\nYFinance:")
        log_info_raw(f"  - Status: {'✅ Enabled' if self.yfinance_enabled else '❌ Disabled'}")
        log_info_raw(f"  - Cache TTL: {self.yfinance_cache_ttl}s ({self.yfinance_cache_ttl/60:.1f} min)")
        log_info_raw(f"  - Request Timeout: {self.yfinance_request_timeout}s")
        
        log_info_raw(f"\nAgents:")
        log_info_raw(f"  Fundamental Agent:")
        log_info_raw(f"    - Status: {'✅ Enabled' if self.fundamental_agent_enabled else '❌ Disabled'}")
        log_info_raw(f"    - Default Depth: {self.fundamental_agent_default_depth}")
        log_info_raw(f"  Technical Agent:")
        log_info_raw(f"    - Status: {'✅ Enabled' if self.technical_agent_enabled else '❌ Disabled'}")
        log_info_raw(f"    - Price Period: {self.technical_agent_price_period}")
        log_info_raw(f"    - Price Interval: {self.technical_agent_price_interval}")
        log_info_raw(f"  News & Sentiment Agent:")
        log_info_raw(f"    - Status: {'✅ Enabled' if self.news_agent_enabled else '❌ Disabled'}")
        log_info_raw(f"    - Lookback: {self.news_agent_lookback_days} days")
        log_info_raw(f"    - Max Articles: {self.news_agent_max_articles}")
        log_info_raw(f"  Aggregation Agent:")
        log_info_raw(f"    - Status: {'✅ Enabled' if self.aggregation_agent_enabled else '❌ Disabled'}")
        log_info_raw(f"    - Use LLM: {'✅ Yes' if self.aggregation_agent_use_llm else '❌ No'}")
        
        log_info_raw(f"\nExecution:")
        log_info_raw(f"  - TTL: {self.execution_ttl_seconds}s ({self.execution_ttl_seconds/3600:.1f}h)")
        log_info_raw(f"  - Max Concurrent: {self.execution_max_concurrent}")
        log_info_raw(f"  - Task Timeout: {self.execution_task_timeout}s ({self.execution_task_timeout/60:.0f} min)")
        log_info_raw(f"  - Soft Timeout: {self.execution_soft_timeout}s ({self.execution_soft_timeout/60:.0f} min)")
        
        log_info_raw(f"\nLLM:")
        log_info_raw(f"  - Model: {self.llm_model}")
        log_info_raw(f"  - API Key: {'✅ Set' if self.openai_api_key else '❌ Not set'}")
        
        log_info_raw("\n" + "=" * 70 + "\n")
    
    # =================================================================
    # Export
    # =================================================================
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary (safe for logging, no secrets)"""
        return {
            "app": {
                "name": self.app_name,
                "environment": self.environment,
                "debug": self.debug,
                "log_level": self.log_level,
            },
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "prefix": self.api_prefix,
                "cors_origins": self.cors_origins,
            },
            "redis": {
                "host": self.redis_host,
                "port": self.redis_port,
                "db": self.redis_db,
                "password_set": bool(self.redis_password),
            },
            "celery": {
                "broker": self.celery_broker,
                "backend": self.celery_backend,
            },
            "api_keys": {
                "openai_set": bool(self.openai_api_key),
                "alpha_vantage_set": bool(self.alpha_vantage_key),
                "finnhub_set": bool(self.finnhub_key),
                "twelve_data_set": bool(self.twelve_data_key),
                "fmp_set": bool(self.fmp_key),
            },
            "supabase": {
                "url_set": bool(self.supabase_url),
                "key_set": bool(self.supabase_key),
                "service_key_set": bool(self.supabase_service_key),
            },
            "yfinance": {
                "enabled": self.yfinance_enabled,
                "cache_ttl": self.yfinance_cache_ttl,
                "request_timeout": self.yfinance_request_timeout,
            },
            "agents": {
                "fundamental": {
                    "enabled": self.fundamental_agent_enabled,
                    "default_depth": self.fundamental_agent_default_depth,
                },
                "technical": {
                    "enabled": self.technical_agent_enabled,
                    "price_period": self.technical_agent_price_period,
                    "price_interval": self.technical_agent_price_interval,
                },
                "news": {
                    "enabled": self.news_agent_enabled,
                    "lookback_days": self.news_agent_lookback_days,
                    "max_articles": self.news_agent_max_articles,
                },
                "aggregation": {
                    "enabled": self.aggregation_agent_enabled,
                    "use_llm": self.aggregation_agent_use_llm,
                },
            },
            "execution": {
                "ttl_seconds": self.execution_ttl_seconds,
                "max_concurrent": self.execution_max_concurrent,
                "task_timeout": self.execution_task_timeout,
                "soft_timeout": self.execution_soft_timeout,
            },
            "llm": {
                "model": self.llm_model,
                "api_key_set": bool(self.openai_api_key),
            },
        }


# =================================================================
# Module-level loader (convenience)
# =================================================================

def load_settings(config_file: str = None) -> Settings:
    """
    Load application settings
    
    Args:
        config_file: Optional path to YAML config file
    
    Returns:
        Settings instance
    """
    return Settings.load(config_file)


# Global settings instance
settings = Settings.load()