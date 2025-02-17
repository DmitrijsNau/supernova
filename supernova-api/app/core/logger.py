import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.definition import ROOT_DIR

log_dir = ROOT_DIR / "logs"

os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    handlers=[TimedRotatingFileHandler(os.path.join(log_dir, "fastapi.log"), when="W0", backupCount=10)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
