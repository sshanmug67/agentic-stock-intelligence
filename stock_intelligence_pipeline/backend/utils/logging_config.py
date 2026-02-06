"""
Logging Configuration for Stock Intelligence Pipeline

Provides:
- Console + file logging (3 log files: all, warnings, errors)
- Raw/unformatted logging helpers
- JSON logging helpers
- Special dedicated loggers for specific activities
- Centralized logger control via YAML config
- Hugging Face Spaces compatibility (console-only mode)

File location: backend/utils/logging_config.py
Log directory: stock_intelligence_pipeline/logs/
"""
import logging
import os
import sys
from pathlib import Path  
from typing import Optional, Dict, Any
import json
from datetime import datetime, date


# ============================================================================
# HUGGING FACE SPACES DETECTION
# ============================================================================
IS_HF_SPACE = os.getenv("SPACE_ID") is not None

if IS_HF_SPACE:
    print("🚀 Hugging Face Spaces detected - File logging disabled, console only")


class ConditionalFormatter(logging.Formatter):
    """Formatter that can output raw or formatted messages"""
    
    def format(self, record):
        # Check if this record should be raw (unformatted)
        if getattr(record, 'raw', False):
            return record.getMessage()
        return super().format(record)


def get_project_root():
    """
    Get the project root directory dynamically
    
    This file is in: stock_intelligence_pipeline/backend/utils/logging_config.py
    Project root is 3 levels up: utils/ -> backend/ -> stock_intelligence_pipeline/
    """
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    return project_root


def get_log_dir():
    """Get log directory at project root (HF Spaces safe)"""
    if IS_HF_SPACE:
        return None
    return str(get_project_root() / "logs")


# ============================================================================
# CENTRALIZED LOGGER CONTROL
# ============================================================================

def _load_logger_config() -> Dict[str, bool]:
    """
    Load logger configuration from YAML file
    
    Looks for: stock_intelligence_pipeline/config/logger_config.yaml
    
    Returns:
        Dictionary of logger names to enabled status
    """
    try:
        import yaml
        config_path = get_project_root() / "config" / "logger_config.yaml"
        
        if not config_path.exists():
            return {}
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('special_loggers', {})
    except Exception:
        return {}


def _is_special_logger_enabled(logger_name: str) -> bool:
    """
    Check if a special logger is enabled in centralized YAML config
    
    Args:
        logger_name: Name of the special logger
        
    Returns:
        True if enabled, False otherwise
    """
    config = _load_logger_config()
    return config.get(logger_name, True)


def setup_logging(
    log_file_name: str = "stock_intel", 
    log_dir: str = None, 
    console_level: int = logging.INFO,
    enable_console: bool = True,
    fresh_start: bool = False
):
    """
    Setup logging with HF Spaces compatibility
    
    Args:
        log_file_name: Base name for log files (ignored in HF Spaces)
        log_dir: Directory for log files (ignored in HF Spaces)
        console_level: Logging level for console
        enable_console: Enable console output (always True in HF Spaces)
        fresh_start: Delete old logs (ignored in HF Spaces)
    """
    root = logging.getLogger()

    # Avoid duplicate handlers 
    if root.hasHandlers():
        root.handlers.clear()

    # Master control
    root.setLevel(logging.INFO)
    
    # === SILENCE NOISY THIRD-PARTY LOGGERS ===
    noisy_loggers = [
        'urllib3', 'urllib3.connectionpool',
        'huggingface_hub', 'sentence_transformers', 'transformers',
        'chromadb', 'openai', 'instructor',
        'hpack.hpack', 'hpack.table',
        'httpcore.http11', 'httpcore.connection',
        'charset_normalizer', 'asyncio',
        'httpx',
        # Stock Intelligence specific
        'yfinance', 'peewee',
        'celery', 'celery.worker', 'celery.app.trace',
        'kombu', 'amqp',
        'redis',
    ]
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Use ConditionalFormatter for all handlers
    formatter = ConditionalFormatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ========================================================================
    # HUGGING FACE SPACES: CONSOLE ONLY
    # ========================================================================
    if IS_HF_SPACE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)
        print(f"✓ Console logging configured (level: {logging.getLevelName(console_level)})")
        return
    
    # ========================================================================
    # LOCAL DEVELOPMENT: CONSOLE + FILE LOGGING
    # ========================================================================
    
    # Console handler - with UTF-8 encoding
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        try:
            console_handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
        except Exception:
            pass
        root.addHandler(console_handler)
    
    # Determine the full log directory path
    if log_dir is None:
        full_log_dir = get_log_dir()
    elif os.path.isabs(log_dir):
        full_log_dir = log_dir
    else:
        full_log_dir = str(get_project_root() / log_dir)
    
    # Ensure directory exists
    os.makedirs(full_log_dir, exist_ok=True)

    all_file_name = os.path.join(full_log_dir, f"{log_file_name}_all_messages.log")
    warning_file_name = os.path.join(full_log_dir, f"{log_file_name}_warnings.log")
    error_file_name = os.path.join(full_log_dir, f"{log_file_name}_errors.log")

    # Handle fresh_start - safe on Windows
    if fresh_start:
        for log_file in [all_file_name, warning_file_name, error_file_name]:
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                except PermissionError:
                    print(f"⚠️  Log file locked (in use): {log_file}")
                    print(f"   Continuing with existing file...")
                except Exception as e:
                    print(f"⚠️  Could not delete {log_file}: {e}")
    
    # File handler 1 - all messages
    all_handler = logging.FileHandler(all_file_name, encoding='utf-8')
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(formatter)
    root.addHandler(all_handler)
    
    # File handler 2 - warnings only
    warning_handler = logging.FileHandler(warning_file_name, encoding='utf-8')
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(formatter)
    root.addHandler(warning_handler)
    
    # File handler 3 - errors only
    error_handler = logging.FileHandler(error_file_name, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)


def shutdown_logging():
    """Flush and close all logging handlers."""
    logging.shutdown()


def setup_fresh_logging(
    log_file_name: str = "stock_intel", 
    log_dir: str = "logs", 
    console_level: int = logging.INFO,
    enable_console: bool = True
):
    """
    Setup fresh logging with deleted old files (HF Spaces safe)
    
    NOTE: In HF Spaces, this just sets up console logging (no files)
    """
    if IS_HF_SPACE:
        setup_logging(
            log_file_name=log_file_name,
            console_level=console_level,
            enable_console=True,
            fresh_start=False
        )
        return
    
    # Local: Ensure directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    setup_logging(
        log_file_name=log_file_name, 
        log_dir=log_dir,
        console_level=console_level,
        enable_console=enable_console,
        fresh_start=True
    )


# === HELPER FUNCTIONS FOR EASY RAW LOGGING ===
def log_raw(message, level=logging.INFO):
    """Log a raw (unformatted) message"""
    logger = logging.getLogger()
    safe_message = str(message).encode('utf-8', errors='replace').decode('utf-8')
    logger.log(level, safe_message, extra={'raw': True})


def log_debug_raw(message):
    log_raw(message, logging.DEBUG)


def log_info_raw(message):
    log_raw(message, logging.INFO)


def log_warning_raw(message):
    log_raw(message, logging.WARNING)


def log_error_raw(message):
    log_raw(message, logging.ERROR)


# === JSON SERIALIZATION HELPER ===
def json_serializer(obj: Any) -> str:
    """Handle non-serializable objects for JSON logging"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    elif hasattr(obj, '__dict__'):
        return str(obj)
    return str(obj)


# === JSON LOGGING HELPERS ===
def log_json_raw(
    data: Dict[str, Any],
    label: Optional[str] = None,
    indent: int = 2,
    level: int = logging.INFO,
    include_borders: bool = True
):
    """
    Log a dictionary/object as formatted JSON
    
    Args:
        data: Dictionary or object to log
        label: Optional label to print before JSON
        indent: JSON indentation (default: 2)
        level: Logging level (default: INFO)
        include_borders: Whether to include separator lines
    """
    logger = logging.getLogger()
    
    try:
        json_str = json.dumps(data, indent=indent, default=json_serializer, ensure_ascii=False)
        
        if include_borders:
            log_raw("=" * 70, level)
        
        if label:
            log_raw(f"📋 {label}", level)
            if include_borders:
                log_raw("=" * 70, level)
        
        log_raw(json_str, level)
        
        if include_borders:
            log_raw("=" * 70, level)
            
    except Exception as e:
        log_raw(f"❌ Error serializing JSON: {e}", logging.ERROR)
        log_raw(f"Data: {str(data)[:500]}...", logging.ERROR)


def log_json_compact(
    data: Dict[str, Any],
    label: Optional[str] = None,
    level: int = logging.INFO
):
    """
    Log a dictionary as compact JSON (no indentation)
    
    Args:
        data: Dictionary to log
        label: Optional label
        level: Logging level
    """
    try:
        json_str = json.dumps(data, default=json_serializer, ensure_ascii=False)
        
        if label:
            log_raw(f"{label}: {json_str}", level)
        else:
            log_raw(json_str, level)
            
    except Exception as e:
        log_raw(f"❌ Error serializing JSON: {e}", logging.ERROR)


# === SPECIAL LOGGING WITH UNIQUE LOGGER NAMES ===
def setup_special_logging(
    log_file_name: str = "special_log_file",
    logger_name: Optional[str] = None,
    fresh_start: bool = False
):
    """
    Setup dedicated logger for monitoring specific activities (HF Spaces safe)
    
    Args:
        log_file_name: Name of the log file (without extension)
        logger_name: Unique logger name (defaults to log_file_name if not provided)
        fresh_start: If True, delete existing log file
        
    Returns:
        Logger instance
    """
    if logger_name is None:
        logger_name = f"special.{log_file_name}"
    
    special_logger = logging.getLogger(logger_name)
    
    # Skip if already configured
    if special_logger.hasHandlers():
        return special_logger
    
    special_logger.setLevel(logging.INFO)
    special_logger.propagate = False
    
    formatter = ConditionalFormatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # HF Spaces: Console handler only
    if IS_HF_SPACE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        special_logger.addHandler(console_handler)
        return special_logger
    
    # Local: File handler
    full_log_dir = get_log_dir()
    special_file = os.path.join(full_log_dir, f"{log_file_name}.log")
    
    if fresh_start and os.path.exists(special_file):
        try:
            os.remove(special_file)
        except PermissionError:
            print(f"⚠️  Special log file locked: {special_file}")
        except Exception as e:
            print(f"⚠️  Could not delete special log: {e}")
    
    special_handler = logging.FileHandler(special_file, encoding='utf-8')
    special_handler.setLevel(logging.INFO)
    special_handler.setFormatter(formatter)
    special_logger.addHandler(special_handler)
    
    return special_logger


def log_special_raw(
    message, 
    logger_name: str = "special.special_log_file",
    include_borders: bool = False
):
    """
    Log raw message to dedicated special log (CHECKS CENTRALIZED CONFIG)
    
    Args:
        message: Message to log
        logger_name: Name of the logger to use
        include_borders: Whether to include separator lines
    """
    clean_logger_name = logger_name.replace("special.", "")
    
    if not _is_special_logger_enabled(clean_logger_name):
        return
    
    logger = logging.getLogger(logger_name)
    safe_message = str(message).encode('utf-8', errors='replace').decode('utf-8')
    
    if include_borders:
        logger.info("=" * 70, extra={'raw': True})
    
    logger.info(safe_message, extra={'raw': True})
    
    if include_borders:
        logger.info("=" * 70, extra={'raw': True})


def log_special_json(
    data: Dict[str, Any],
    logger_name: str = "special.special_log_file",
    label: Optional[str] = None,
    indent: int = 2,
    include_borders: bool = True
):
    """
    Log JSON to a special logger (CHECKS CENTRALIZED CONFIG)
    
    Args:
        data: Dictionary to log
        logger_name: Name of special logger
        label: Optional label
        indent: JSON indentation
        include_borders: Whether to include separator lines
    """
    clean_logger_name = logger_name.replace("special.", "")
    
    if not _is_special_logger_enabled(clean_logger_name):
        return
    
    logger = logging.getLogger(logger_name)
    
    try:
        json_str = json.dumps(data, indent=indent, default=json_serializer, ensure_ascii=False)
        safe_json = json_str.encode('utf-8', errors='replace').decode('utf-8')
        
        if include_borders:
            logger.info("=" * 70, extra={'raw': True})
        
        if label:
            logger.info(f"📋 {label}", extra={'raw': True})
            if include_borders:
                logger.info("=" * 70, extra={'raw': True})
        
        logger.info(safe_json, extra={'raw': True})
        
        if include_borders:
            logger.info("=" * 70, extra={'raw': True})
            
    except Exception as e:
        logger.error(f"❌ Error serializing JSON: {e}", extra={'raw': True})
        logger.error(f"Data: {str(data)[:500]}...", extra={'raw': True})