import logging
from enum import Enum

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from geo_lib.daemon.database.connection import CursorFromConnectionFromPool

_logger = logging.getLogger("MAIN").getChild("DBLOG")


class DatabaseLogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class DatabaseLogSource(Enum):
    IMPORT = "import"


class DatabaseLogItem(BaseModel):
    # Using an object so we can add arbitrary data if nessesary.
    msg: str
    level: DatabaseLogLevel


_SQL_INSERT_LOG_ITEM = "INSERT INTO public.geologs (user_id, level, text, source) VALUES (%s, %s, %s, %s)"


def log_to_db(msg: str, level: DatabaseLogLevel, user_id: int, source: DatabaseLogSource):
    _logger.log(level.value, msg)
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(_SQL_INSERT_LOG_ITEM, (user_id, level.value, msg, source.value))
