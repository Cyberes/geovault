from django.urls import path

from data.views.import_item import upload_item, fetch_import_queue, fetch_queued, delete_import_queue, update_imported_item

urlpatterns = [
    path('item/import/upload/', upload_item, name='upload_file'),
    path('item/import/get/<int:item_id>', fetch_import_queue, name='fetch_import_queue'),
    path('item/import/get/mine', fetch_queued, name='fetch_queued'),
    path('item/import/delete/<int:id>', delete_import_queue, name='delete_import_queue'),
    path('item/import/update/<int:item_id>', update_imported_item),
]
