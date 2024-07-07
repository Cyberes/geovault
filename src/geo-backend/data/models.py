from django.contrib.auth import get_user_model
from django.db import models


class ImportQueue(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    geofeatures = models.JSONField(default=dict)
    original_filename = models.TextField()
    raw_kml = models.TextField()
    raw_kml_hash = models.CharField(max_length=64, unique=True)
    data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
