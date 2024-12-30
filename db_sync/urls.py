from django.urls import path

from .views import (SyncDatabaseView, SyncSingleAuctionView)

urlpatterns = [
    path('', SyncDatabaseView.as_view(), name='sync_database'),
    path('single/', SyncSingleAuctionView.as_view(), name='sync_single_auction'),
]
