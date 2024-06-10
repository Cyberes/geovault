from django.urls import path

from data.views.import_item import upload_item, fetch_import_queue, fetch_queued

urlpatterns = [
    path('item/import/upload/', upload_item, name='upload_file'),
    path('item/import/get/<int:id>', fetch_import_queue, name='fetch_import_queue'),
    path('item/import/get/mine', fetch_queued, name='fetch_queued'),
]
