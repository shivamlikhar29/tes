from functools import wraps
from django.http import HttpResponseForbidden

UNIT_TO_GRAMS = {
    "g": 1,
    "kg": 1000,
    "ml": 1,
    "l": 1000,
    "cup": 240,
    "bowl": 300,
    "piece": 100,
    "tbsp": 15,
    "tsp": 5,
    "slice": 30,
    "other": 100,
}


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated or user.role not in allowed_roles:
                return HttpResponseForbidden("Access Denied")
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator