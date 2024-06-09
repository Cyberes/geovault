from django.http import JsonResponse


def check_auth(request):
    if request.user.is_authenticated:
        data = {
            'authorized': True,
            'username': request.user.username,
            'id': request.user.id
        }
    else:
        data = {
            'authorized': False,
            'username': None,
            'id': None
        }
    return JsonResponse(data)
