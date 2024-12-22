from django.urls import path
from .views import (AuctionListView, AuctionDetailView)

urlpatterns = [
    path('', AuctionListView.as_view(), name='auction_list'),
    path('auctions/', AuctionListView.as_view(), name='auction_list'),
    path('auctions/<int:pk>/', AuctionDetailView.as_view(), name='auction_detail'),
]