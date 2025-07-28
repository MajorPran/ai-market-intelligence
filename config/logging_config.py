"""
Advanced logging configuration for AI Market Intelligence Tool
Provides structured logging with multiple outputs and performance monitoring
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any
from config.settings import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        if hasattr(record, 'api_endpoint'):
            log_entry['api_endpoint'] = record.api_endpoint
        if hasattr(record, 'scraper_target'):
            log_entry['scraper_target'] = record.scraper_target

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

class PerformanceFilter(logging.Filter):
    """Filter to highlight performance issues"""

    def filter(self, record):
        # Flag slow operations
        if hasattr(record, 'execution_time') and record.execution_time > 5.0:
            record.levelname = 'SLOW'
            record.message = f"[SLOW OPERATION] {record.getMessage()}"
        return True

class ScraperLoggerAdapter(logging.LoggerAdapter):
    """Custom adapter for scraper-specific logging"""

    def process(self, msg, kwargs):
        return f"[{self.extra['scraper_name']}] {msg}", kwargs

def setup_logging():
    """Configure comprehensive logging system"""

    # Ensure logs directory exists
    settings.LOGS_DIR.mkdir(exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console Handler - Human readable for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # Add performance filter
    performance_filter = PerformanceFilter()
    console_handler.addFilter(performance_filter)

    # File Handler - Detailed logging
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOGS_DIR / 'intelligence.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    # JSON Handler - Structured logs for analysis
    json_handler = logging.handlers.RotatingFileHandler(
        settings.LOGS_DIR / 'intelligence.json',
        maxBytes=10*1024*1024,  # 10MB  
        backupCount=3
    )
    json_handler.setLevel(logging.INFO)
    json_handler.setFormatter(JSONFormatter())

    # Error Handler - Separate file for errors
    error_handler = logging.handlers.RotatingFileHandler(
        settings.LOGS_DIR / 'errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(json_handler)
    root_logger.addHandler(error_handler)

    # Configure specific loggers
    setup_module_loggers()

    # Suppress noisy third-party loggers
    suppress_third_party_logs()

    logging.info("🔧 Logging system initialized")
    logging.info(f"📁 Log files location: {settings.LOGS_DIR}")

def setup_module_loggers():
    """Configure loggers for specific modules"""

    # Scraper logger
    scraper_logger = logging.getLogger('intelligence.scraper')
    scraper_logger.setLevel(logging.DEBUG)

    # LLM Analysis logger
    llm_logger = logging.getLogger('intelligence.llm')
    llm_logger.setLevel(logging.DEBUG)

    # API logger
    api_logger = logging.getLogger('intelligence.api')
    api_logger.setLevel(logging.INFO)

    # Database logger
    db_logger = logging.getLogger('intelligence.database')
    db_logger.setLevel(logging.INFO)

    # Performance logger
    perf_logger = logging.getLogger('intelligence.performance')
    perf_logger.setLevel(logging.INFO)

    # Alert system logger
    alert_logger = logging.getLogger('intelligence.alerts')
    alert_logger.setLevel(logging.INFO)

def suppress_third_party_logs():
    """Reduce noise from third-party libraries"""
    noisy_loggers = [
        'requests.packages.urllib3',
        'urllib3.connectionpool',
        'selenium.webdriver.remote.remote_connection',
        'transformers.tokenization_utils_base',
        'openai._base_client'
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

def get_logger(name: str, **extra_context) -> logging.Logger:
    """Get a logger with optional context"""
    logger = logging.getLogger(f'intelligence.{name}')

    if extra_context:
        return logging.LoggerAdapter(logger, extra_context)

    return logger

def get_scraper_logger(scraper_name: str) -> ScraperLoggerAdapter:
    """Get a specialized logger for scrapers"""
    logger = logging.getLogger('intelligence.scraper')
    return ScraperLoggerAdapter(logger, {'scraper_name': scraper_name})

def log_performance(func_name: str, execution_time: float, **extra):
    """Log performance metrics"""
    perf_logger = logging.getLogger('intelligence.performance')
    perf_logger.info(
        f"Function '{func_name}' completed", 
        extra={'execution_time': execution_time, **extra}
    )

def log_api_request(endpoint: str, method: str, status_code: int, execution_time: float):
    """Log API request details"""
    api_logger = logging.getLogger('intelligence.api')
    level = logging.INFO if status_code < 400 else logging.ERROR

    api_logger.log(
        level,
        f"{method} {endpoint} - {status_code}",
        extra={
            'api_endpoint': endpoint,
            'http_method': method,
            'status_code': status_code,
            'execution_time': execution_time
        }
    )

def log_scraping_result(target: str, success: bool, items_found: int, execution_time: float):
    """Log scraping operation results"""
    scraper_logger = logging.getLogger('intelligence.scraper')
    level = logging.INFO if success else logging.ERROR

    message = f"Scraped {target} - {'Success' if success else 'Failed'}"
    if success:
        message += f" - Found {items_found} items"

    scraper_logger.log(
        level,
        message,
        extra={
            'scraper_target': target,
            'success': success,
            'items_found': items_found,
            'execution_time': execution_time
        }
    )

def log_llm_usage(provider: str, model: str, tokens_used: int, cost_estimate: float = None):
    """Log LLM API usage for cost tracking"""
    llm_logger = logging.getLogger('intelligence.llm')

    message = f"LLM API call - {provider}/{model} - {tokens_used} tokens"
    extra = {
        'llm_provider': provider,
        'llm_model': model, 
        'tokens_used': tokens_used
    }

    if cost_estimate:
        message += f" - ${cost_estimate:.4f}"
        extra['cost_estimate'] = cost_estimate

    llm_logger.info(message, extra=extra)

# Context managers for structured logging
class LogExecutionTime:
    """Context manager to log function execution time"""

    def __init__(self, func_name: str, logger: logging.Logger = None):
        self.func_name = func_name
        self.logger = logger or logging.getLogger('intelligence.performance')
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting {self.func_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            self.logger.error(
                f"{self.func_name} failed after {execution_time:.2f}s",
                extra={'execution_time': execution_time},
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            log_performance(self.func_name, execution_time)

# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()