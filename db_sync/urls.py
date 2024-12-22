from django.urls import path

from .views import (SyncDatabaseView)

urlpatterns = [
    path('', SyncDatabaseView.as_view(), name='sync_database'),
]
