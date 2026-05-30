from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(pattern_name="projects:list", permanent=False)),
    # Подключаем маршруты приложений
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
