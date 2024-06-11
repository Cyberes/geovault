import json
import logging
import time
import traceback
from uuid import uuid4

from psycopg2.extras import RealDictCursor

from geo_lib.daemon.database.connection import CursorFromConnectionFromPool
from geo_lib.daemon.database.locking import DBLockManager
from geo_lib.logging.database import log_to_db, DatabaseLogLevel, DatabaseLogSource
from geo_lib.spatial.kml import kml_to_geojson
from geo_lib.time import get_time_ms

_SQL_GET_UNPROCESSED_ITEMS = "SELECT * FROM public.data_importqueue WHERE geojson = '{}' ORDER BY id ASC"
_SQL_INSERT_PROCESSED_ITEM = "UPDATE public.data_importqueue SET geojson = %s WHERE id = %s"
_SQL_DELETE_ITEM = "DELETE FROM public.data_importqueue WHERE id = %s"

_logger = logging.getLogger("DAEMON").getChild("IMPORTER")


# TODO: support multiple workers

def import_worker():
    worker_id = str(uuid4())
    lock_manager = DBLockManager(worker_id=worker_id)
    while True:
        queue = []
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(_SQL_GET_UNPROCESSED_ITEMS)
            import_queue_items = cursor.fetchall()
            for item in import_queue_items:
                if lock_manager.lock_row('data_importqueue', item['id']):
                    queue.append(item)

        if len(queue):
            _logger.info(f'processing {len(import_queue_items)} items -- {worker_id}')

        for item in queue:
            start = get_time_ms()
            success = False
            try:
                geojson_data, messages = kml_to_geojson(item['raw_kml'])
                success = True
            except Exception as e:
                err_name = e.__class__.__name__
                err_msg = str(e)
                if hasattr(e, 'message'):
                    err_msg = e.message
                msg = f'Failed to import item #{item["id"]} "{item["original_filename"]}", encountered {err_name}. {err_msg}'
                log_to_db(msg, level=DatabaseLogLevel.ERROR, user_id=item['user_id'], source=DatabaseLogSource.IMPORT)
                traceback.print_exc()
                with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(_SQL_DELETE_ITEM, (item['id'],))
            if success:
                with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(_SQL_INSERT_PROCESSED_ITEM, (json.dumps(geojson_data, sort_keys=True), item['id']))
                _logger.info(f'IMPORT: processed #{item["id"]} in {round((get_time_ms() - start) / 1000, 2)} seconds -- {worker_id}')
            lock_manager.unlock_row('data_importqueue', item['id'])

        if not len(queue):
            # Only sleep if there were no items last time we checked.
            time.sleep(5)

# def _process_item_data(item)
