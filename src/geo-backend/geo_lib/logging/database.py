import logging
from enum import Enum

from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from geo_lib.daemon.database.connection import CursorFromConnectionFromPool


class DatabaseLogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class DatabaseLogItem(BaseModel):
    # Using an object so we can add arbitrary data if nessesary.
    msg: str
    level: DatabaseLogLevel


_SQL_INSERT_ITEM = 'INSERT INTO public.data_geologs (user_id, text, source) VALUES (%s, %s, %s)'


def log_to_db(msg: str, level: DatabaseLogLevel, user_id: int, source: str):
    print(msg)
    return
    # TODO:
    with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(_SQL_INSERT_ITEM, (user_id, DatabaseLogItem(msg=msg, level=level).json()))
