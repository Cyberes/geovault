from django.urls import re_path, path

from users.views import register, dashboard, check_auth
from users.views.upload_item import upload_item, fetch_import_queue

urlpatterns = [
    re_path(r"^account/register/", register, name="register"),
    re_path(r"^user/dashboard/", dashboard, name="dashboard"),
    re_path(r"^api/user/status/", check_auth),
    re_path(r'^api/item/import/upload/', upload_item, name='upload_file'),
    path('api/item/import/get/<int:id>', fetch_import_queue, name='fetch_import_queue'),
]
