import hashlib
import json
import traceback

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from data.models import ImportQueue
from geo_lib.daemon.database.locking import DBLockManager
from geo_lib.daemon.workers.workers_lib.importer.kml import kmz_to_kml
from geo_lib.daemon.workers.workers_lib.importer.tagging import generate_auto_tags
from geo_lib.types.feature import GeoPoint, GeoLineString, GeoPolygon
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
def fetch_import_queue(request, item_id):
    if item_id is None:
        return JsonResponse({'success': False, 'msg': 'ID not provided', 'code': 400}, status=400)
    lock_manager = DBLockManager()
    try:
        queue = ImportQueue.objects.get(id=item_id)
        if queue.user_id != request.user.id:
            return JsonResponse({'success': False, 'msg': 'not authorized to view this item', 'code': 403}, status=400)
        if not lock_manager.is_locked('data_importqueue', queue.id) and (len(queue.geofeatures) or len(queue.log)):
            return JsonResponse({'success': True, 'geofeatures': queue.geofeatures, 'log': queue.log, 'msg': None}, status=200)
        return JsonResponse({'success': True, 'geofeatures': [], 'log': [], 'msg': 'uploaded data still processing'}, status=200)
    except ImportQueue.DoesNotExist:
        return JsonResponse({'success': False, 'msg': 'ID does not exist', 'code': 404}, status=400)


@login_required_401
def fetch_queued(request):
    user_items = ImportQueue.objects.exclude(geofeatures__len=0).filter(user=request.user).values('id', 'geofeatures', 'original_filename', 'raw_kml_hash', 'data', 'log', 'timestamp')
    data = json.loads(json.dumps(list(user_items), cls=DjangoJSONEncoder))
    lock_manager = DBLockManager()
    for i, item in enumerate(data):
        count = len(item['geofeatures'])
        item['processing'] = not (len(item['geofeatures']) and len(item['log'])) and lock_manager.is_locked('data_importqueue', item['id'])
        item['feature_count'] = count
        del item['geofeatures']
    return JsonResponse({'data': data, 'msg': None})


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


@login_required_401
@csrf_protect  # TODO: put this on all routes
@require_http_methods(["PUT"])
def update_imported_item(request, item_id):
    try:
        queue = ImportQueue.objects.get(id=item_id)
    except ImportQueue.DoesNotExist:
        return JsonResponse({'success': False, 'msg': 'ID does not exist', 'code': 404}, status=400)
    if queue.user_id != request.user.id:
        return JsonResponse({'success': False, 'msg': 'not authorized to edit this item', 'code': 403}, status=403)

    try:
        data = json.loads(request.body)
        if not isinstance(data, list):
            raise ValueError('Invalid data format. Expected a list.')
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'success': False, 'msg': str(e), 'code': 400}, status=400)

    parsed_data = []
    for feature in data:
        match feature['type'].lower():
            case 'point':
                c = GeoPoint(**feature)
            case 'linestring':
                c = GeoLineString(**feature)
            case 'polygon':
                c = GeoPolygon(**feature)
            case _:
                continue

        # Generate the tags after the user has made their changes.
        c.properties.tags = generate_auto_tags(c)
        parsed_data.append(json.loads(c.model_dump_json()))

    # Erase the geofeatures column
    queue.geofeatures = []

    # Update the data column with the new data
    queue.data = parsed_data

    queue.save()
    return JsonResponse({'success': True, 'msg': 'Item updated successfully'})


def _hash_kml(b: str):
    if not isinstance(b, bytes):
        b = b.encode()
    return hashlib.sha256(b).hexdigest()
