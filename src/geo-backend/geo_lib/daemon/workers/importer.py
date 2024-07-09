import json
import logging
import time
import traceback
from uuid import uuid4

from psycopg2.extras import RealDictCursor

from geo_lib.daemon.database.connection import CursorFromConnectionFromPool
from geo_lib.daemon.database.locking import DBLockManager
from geo_lib.daemon.workers.workers_lib.importer.kml import kml_to_geojson
from geo_lib.daemon.workers.workers_lib.importer.logging import create_import_log_msg
from geo_lib.daemon.workers.workers_lib.importer.tagging import generate_auto_tags
from geo_lib.logging.database import log_to_db, DatabaseLogLevel, DatabaseLogSource
from geo_lib.time import get_time_ms
from geo_lib.types.feature import geojson_to_geofeature

_SQL_GET_UNPROCESSED_ITEMS = "SELECT * FROM public.data_importqueue WHERE geofeatures = '[]' AND log = '[]' ORDER BY id ASC"
_SQL_INSERT_PROCESSED_ITEM = "UPDATE public.data_importqueue SET geofeatures = %s, log = %s WHERE id = %s"
_SQL_DELETE_ITEM = "DELETE FROM public.data_importqueue WHERE id = %s"

_logger = logging.getLogger("DAEMON").getChild("IMPORTER")


# TODO: support multiple workers

def import_worker():
    worker_id = str(uuid4())
    lock_manager = DBLockManager(worker_id)
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
            geofetures = []
            messages = []
            try:
                # The actual import.
                geojson_data, kml_conv_messages = kml_to_geojson(item['raw_kml'])
                messages.extend(kml_conv_messages)
                geofetures, typing_messages = geojson_to_geofeature(geojson_data)
                messages.extend(typing_messages)
                for feature in geofetures:
                    feature.tags = generate_auto_tags(feature)
                success = True
            except Exception as e:
                err_name = e.__class__.__name__
                err_msg = str(e)
                if hasattr(e, 'message'):
                    err_msg = e.message
                msg = f'Failed to import item #{item["id"]} "{item["original_filename"]}", encountered {err_name}. {err_msg}'
                messages.append(create_import_log_msg(f'{err_name}: {err_msg}'))
                log_to_db(msg, level=DatabaseLogLevel.ERROR, user_id=item['user_id'], source=DatabaseLogSource.IMPORT)
                traceback.print_exc()
            features = []  # dummy data
            if success:
                features = [json.loads(x.model_dump_json()) for x in geofetures]
            with CursorFromConnectionFromPool(cursor_factory=RealDictCursor) as cursor:
                data = json.dumps(features)
                cursor.execute(_SQL_INSERT_PROCESSED_ITEM, (data, json.dumps(messages), item['id']))
            lock_manager.unlock_row('data_importqueue', item['id'])
            _logger.info(f'IMPORT: processed #{item["id"]} in {round((get_time_ms() - start) / 1000, 2)} seconds -- {worker_id}')

        if not len(queue):
            # Only sleep if there were no items last time we checked.
            time.sleep(5)
