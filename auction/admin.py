from django.contrib import admin
from .models import AuctionItem, Bid

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ('user', 'offer', 'date')
    ordering = ['-date']

@admin.register(AuctionItem)
class AuctionItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'name', 'price', 'start_date', 'end_date', 'uri', 'mini_photo', 'status', 'category', 'currency')
    inlines = [BidInline]
    exclude = ()
    list_display = ('name', 'status', 'get_bid_count')
    list_filter = ('status',)

    def get_bid_count(self, obj):
        return Bid.objects.filter(auction_item=obj).count()
    get_bid_count.short_description = 'Bid Count'

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    readonly_fields = ('auction_item', 'user', 'offer', 'date')
    exclude = ()
