from django.http import JsonResponse

from geo_lib.website.auth import login_required_401


@login_required_401
def dashboard(request):
    data = {
        "username": request.user.username,
        "id": request.user.id
    }
    return JsonResponse(data)
