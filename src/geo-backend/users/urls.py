from django.urls import re_path, include, path

from users.views import register, index

urlpatterns = [
    path('', index),
    re_path(r"^account/", include("django.contrib.auth.urls")),
    re_path(r"^register/", register, name="register"),
]
