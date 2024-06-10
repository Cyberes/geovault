from django.contrib.auth import get_user_model
from django.db import models


class ImportQueue(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    geojson = models.JSONField(default=dict)
    original_filename = models.TextField()
    raw_kml = models.TextField()
    raw_kml_hash = models.CharField(max_length=64, unique=True)
    data = models.JSONField(default=dict)
    worker_lock = models.TextField(default=None, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class GeoLogs(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.JSONField()
    source = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
