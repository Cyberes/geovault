import hashlib
import json
import traceback

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse

from data.models import ImportQueue
from geo_lib.spatial.kml import kmz_to_kml
from geo_lib.website.auth import login_required_401


class DocumentForm(forms.Form):
    file = forms.FileField()


@login_required_401
def upload_item(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            # Check file size
            # TODO: config??
            if uploaded_file.size > 100 * 1024 * 1024:  # file size limit 100MB
                return JsonResponse({'success': False, 'msg': 'File size must be less than 100MB', 'id': None}, status=400)

            file_data = uploaded_file.read()
            file_name = uploaded_file.name

            try:
                kml_doc = kmz_to_kml(file_data)
            except Exception as e:
                print(traceback.format_exc())  # TODO: logging
                return JsonResponse({'success': False, 'msg': 'failed to parse KML/KMZ', 'id': None}, status=400)

            try:
                import_queue, created = ImportQueue.objects.get_or_create(raw_kml=kml_doc, raw_kml_hash=_hash_kml(kml_doc), original_filename=file_name, user=request.user)
                import_queue.save()
            except IntegrityError:
                created = False
                import_queue = ImportQueue.objects.get(
                    raw_kml=kml_doc,
                    raw_kml_hash=_hash_kml(kml_doc),
                    # original_filename=file_name,
                    user=request.user
                )
            msg = 'upload successful'
            if not created:
                msg = 'data already exists in the import queue'
            return JsonResponse({'success': True, 'msg': msg, 'id': import_queue.id}, status=200)

            # TODO: put the processed data into the database and then return the ID so the frontend can go to the import page and use the ID to start the import
        else:
            return JsonResponse({'success': False, 'msg': 'invalid upload structure', 'id': None}, status=400)

    else:
        return HttpResponse(status=405)


@login_required_401
def fetch_import_queue(request, id):
    if id is None:
        return JsonResponse({'success': False, 'msg': 'ID not provided', 'code': 400}, status=400)
    try:
        queue = ImportQueue.objects.get(id=id)
        if queue.user_id != request.user.id:
            return JsonResponse({'success': False, 'msg': 'not authorized to view this item', 'code': 403}, status=400)
        if len(queue.geojson):
            return JsonResponse({'success': True, 'geojson': queue.geojson}, status=200)
        return JsonResponse({'success': True, 'geojson': {}, 'msg': 'uploaded data still processing'}, status=200)
    except ImportQueue.DoesNotExist:
        return JsonResponse({'success': False, 'msg': 'ID does not exist', 'code': 404}, status=400)


@login_required_401
def fetch_queued(request):
    user_items = ImportQueue.objects.filter(user=request.user).values('id', 'geojson', 'original_filename', 'raw_kml_hash', 'data', 'timestamp')
    data = json.loads(json.dumps(list(user_items), cls=DjangoJSONEncoder))
    for i, item in enumerate(data):
        count = len(item['geojson'].get('features', []))
        item['processing'] = len(item['geojson']) == 0
        item['feature_count'] = count
        del item['geojson']
    return JsonResponse({'data': data})


@login_required_401
def delete_import_queue(request, id):
    if request.method == 'DELETE':
        try:
            queue = ImportQueue.objects.get(id=id)
        except ImportQueue.DoesNotExist:
            return JsonResponse({'success': False, 'msg': 'ID does not exist', 'code': 404}, status=400)
        queue.delete()
        return JsonResponse({'success': True})
    return HttpResponse(status=405)


def _hash_kml(b: str):
    if not isinstance(b, bytes):
        b = b.encode()
    return hashlib.sha256(b).hexdigest()
