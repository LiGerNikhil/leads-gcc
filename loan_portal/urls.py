from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from loans.views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    account_activate,
    page_not_found,
    server_error,
    permission_denied,
    bad_request,
)

handler404 = page_not_found
handler500 = server_error
handler403 = permission_denied
handler400 = bad_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/activate/<uidb64>/<token>/', account_activate, name='account_activate'),
    path('', include('loans.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
