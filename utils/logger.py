import logging
import uuid
import structlog
from logging.handlers import RotatingFileHandler

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler("bot.log", encoding="utf-8")
        ]
    )
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

def get_logger(name: str):
    return structlog.get_logger(name)

def get_request_logger(name: str, user_id: int = None):
    request_id = str(uuid.uuid4())[:8]
    logger = structlog.get_logger(name)
    return logger.bind(request_id=request_id, user_id=user_id)