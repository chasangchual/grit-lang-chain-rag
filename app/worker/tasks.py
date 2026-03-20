from __future__ import annotations
from pathlib import Path 
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config.config import get_config
from app.config.db import get_session
