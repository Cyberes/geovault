from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpResponse, JsonResponse

from geo_lib.spatial.kml import kml_to_geojson


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


class DocumentForm(forms.Form):
    file = forms.FileField()


class ImportQueue(models.Model):
    data = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'import_queue'


def upload_item(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_data = uploaded_file.read()

            try:
                geojson = kml_to_geojson(file_data)
                import_queue, created = ImportQueue.objects.get_or_create(data=geojson, user=request.user)
                import_queue.save()
                msg = 'upload successful'
                if not created:
                    msg = 'data already exists in the import queue'
                return JsonResponse({'success': True, 'msg': msg, 'id': import_queue.id}, status=200)
            except Exception as e:
                print(e)  # TODO: logging
                return JsonResponse({'success': False, 'msg': 'failed to parse KML/KMZ', 'id': None}, status=400)

            # TODO: put the processed data into the database and then return the ID so the frontend can go to the import page and use the ID to start the import
        else:
            return JsonResponse({'success': False, 'msg': 'invalid upload structure', 'id': None}, status=400)

    else:
        return HttpResponse(status=405)


def fetch_import_queue(request, id):
    if id is None:
        return JsonResponse({'success': False, 'msg': 'ID not provided', 'code': 400}, status=400)
    try:
        queue = ImportQueue.objects.get(id=id)
        if queue.user_id != request.user.id:
            return JsonResponse({'success': False, 'msg': 'not authorized to view this item', 'code': 403}, status=400)
        return JsonResponse({'success': True, 'data': queue.data}, status=200)
    except ImportQueue.DoesNotExist:
        return JsonResponse({'success': False, 'msg': 'ID does not exist', 'code': 404}, status=400)
