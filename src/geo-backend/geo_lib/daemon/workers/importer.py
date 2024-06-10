import json
import time
import traceback
from uuid import uuid4

from psycopg2.extras import RealDictCursor

from geo_lib.daemon.database.connection import CursorFromConnectionFromPool
from geo_lib.logging.database import log_to_db, DatabaseLogLevel
from geo_lib.spatial.kml import kml_to_geojson
from geo_lib.time import get_time_ms

_SQL_GET_UNPROCESSED_ITEMS = "SELECT * FROM public.data_importqueue ORDER BY id ASC"  # coordinates
_SQL_INSERT_PROCESSED_ITEM = "UPDATE public.data_importqueue SET geojson = %s WHERE id = %s"


# TODO: support multiple workers

def import_worker():
    worker_id = str(uuid4())
    while True:
        with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(_SQL_GET_UNPROCESSED_ITEMS)
            import_queue_items = cursor.fetchall()

        if len(import_queue_items):
            print(f'IMPORT: processing {len(import_queue_items)} items')  # TODO: logging, also log worker ID

        for item in import_queue_items:
            start = get_time_ms()
            try:
                geojson_data, messages = kml_to_geojson(item['raw_kml'])
            except Exception as e:
                err_name = e.__class__.__name__
                err_msg = str(e)
                if hasattr(e, 'message'):
                    err_msg = e.message
                msg = f'Failed to import item #{item["id"]}, encountered {err_name}. {err_msg}'
                log_to_db(msg, level=DatabaseLogLevel.ERROR, user_id=item['user_id'])
                traceback.print_exc()
                continue
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(_SQL_INSERT_PROCESSED_ITEM, (json.dumps(geojson_data, sort_keys=True), item['id']))
            print(f'IMPORT: processed #{item["id"]} in {round((get_time_ms() - start) / 1000, 2)} seconds')  # TODO: logging, also log worker ID

        if not len(import_queue_items):
            # Only sleep if there were no items last time we checked.
            time.sleep(5)

# def _process_item_data(item)
