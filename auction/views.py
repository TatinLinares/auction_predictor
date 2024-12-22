import json
import math
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from .models import AuctionItem, Bid

class AuctionDetailView(DetailView):
    model = AuctionItem
    template_name = 'auction/auction_detail.html'
    context_object_name = 'auction_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bids = Bid.objects.filter(auction_item=self.object).order_by('date')
        
        auction_end = self.object.end_date or timezone.now()
        total_auction_duration = (auction_end - self.object.start_date).total_seconds() / 60
        processed_bids = []
        
        if bids:
            # Logarithmic scaling function
            def log_scale_time(time_diff):
                if time_diff == 0:
                    return 0
                # Use log scaling with a small offset to prevent log(0)
                return 10 * math.log10(time_diff + 1)
            
            # Process bids with logarithmic time scaling
            current_time = 0
            for i, bid in enumerate(bids):
                if i == 0:
                    processed_time = 0
                else:
                    # Calculate time difference from previous bid
                    time_diff = (bid.date - bids[i-1].date).total_seconds() / 60
                    processed_time = current_time + log_scale_time(time_diff)
                
                current_time = processed_time
                
                processed_bids.append({
                    'time_elapsed': processed_time,
                    'price': bid.offer,
                    'date': bid.date.strftime('%Y-%m-%d %H:%M:%S'),
                    'user': bid.user,
                })
            
            # Normalize time to auction duration
            max_processed_time = processed_bids[-1]['time_elapsed']
            for bid in processed_bids:
                bid['time_elapsed'] = bid['time_elapsed'] * (total_auction_duration / max_processed_time)
            
            initial_price = bids[0].offer
            max_bid = max(bid.offer for bid in bids)
        else:
            initial_price = self.object.price
            max_bid = initial_price
            processed_bids = []
        
        context['bid_data_json'] = json.dumps({
            'bids': processed_bids,
            'initial_price': initial_price,
            'total_auction_duration': total_auction_duration,
            'max_bid': max_bid,
            'total_bids': len(bids)
        })
        
        context['initial_price'] = f"{initial_price:,.0f}".replace(",", ".").replace(".", ",")
        context['current_status'] = self.object.status
        context['total_unique_bidders'] = bids.values('user').distinct().count()
        
        return context
    

class AuctionListView(ListView):
    model = AuctionItem
    template_name = 'auction/auction_list.html'
    context_object_name = 'auctions'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = AuctionItem.objects.annotate(
            bid_count=Count('bid'),
            latest_bid=Coalesce(Max('bid__offer'), 'price'),
            unique_bidders=Count('bid__user', distinct=True)
        )
        
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.exclude(status__in=['ended', 'suspended']).order_by(
                Case(
                    When(end_date__isnull=False, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                'end_date'
            )
        elif status_filter == 'ended':
            queryset = queryset.filter(status='ended').order_by(
                Case(
                    When(end_date__isnull=False, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                '-end_date' 
            )
        else:
            queryset = queryset.order_by(
                Case(
                    When(status='ended', then=2),
                    When(status='suspended', then=1),
                    default=0,
                    output_field=IntegerField(),
                ),
                Case(
                    When(end_date__isnull=False, then=0),
                    default=1,
                    output_field=IntegerField(),
                ),
                Coalesce('end_date', now()).desc()
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'all')
        return context
