from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("core.urls")),
    path("login/", core_views.CustomLoginView.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
]

handler404 = "core.views.custom_404"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        re_path(r"^.*$", lambda request: core_views.custom_404(request, None))
    ]
