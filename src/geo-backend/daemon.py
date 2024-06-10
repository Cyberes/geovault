import threading
import time

from geo_lib.daemon.database.connection import Database
from geo_lib.daemon.workers.importer import import_worker

# TODO: config
Database.initialise(minconn=1, maxconn=100, host='h.postgres.nb', database='geobackend', user='geobackend', password='juu1waigu1pookee1ohcierahMoofie3')

import_thread = threading.Thread(target=import_worker)
import_thread.start()

while True:
    time.sleep(3600)
