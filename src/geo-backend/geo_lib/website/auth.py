from functools import wraps

from django.http import HttpResponse


def login_required_401(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)

    return _wrapped_view
