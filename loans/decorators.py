from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login') + '?next=' + request.path)
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.role not in allowed_roles:
                messages.error(
                    request,
                    'You do not have permission to access this resource.'
                )
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def super_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login') + '?next=' + request.path)
        if request.user.is_superuser or request.user.role == 'SUPER_ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You do not have permission to access this resource.')
        return redirect('dashboard')
    return _wrapped_view


def gcc_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login') + '?next=' + request.path)
        if request.user.is_superuser or request.user.role in ('SUPER_ADMIN', 'GCC_NOIDA'):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You do not have permission to access this resource.')
        return redirect('dashboard')
    return _wrapped_view
