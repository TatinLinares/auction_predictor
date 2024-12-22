from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', include('auction.urls')),
    path('admin/', admin.site.urls),
    path('db_sync/', include('db_sync.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
