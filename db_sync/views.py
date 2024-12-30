from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .utils import sync_ended_auctions, sync_active_auctions, sync_single_auction, extract_auction_id

class SyncSingleAuctionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        auction_url = request.POST.get('auction_url')
        try:
            auction_id = extract_auction_id(auction_url)
            if not auction_id:
                messages.error(request, 'Invalid auction URL format')
                return redirect('sync_database')
            
            item_id = sync_single_auction(auction_id)
            messages.success(request, f'Auction synchronized successfully')
            return redirect(reverse_lazy('auction_detail', kwargs={'pk': item_id}))
            
        except Exception as e:
            messages.error(request, f'Failed to sync auction: {str(e)}')
            return redirect('sync_database')

class SyncDatabaseView(LoginRequiredMixin, TemplateView):
    template_name = 'sync/sync.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sync_url'] = reverse_lazy('sync_database')
        context['sync_options'] = [
            {'value': 'ended', 'label': 'Ended Auctions'},
            {'value': 'active', 'label': 'Active Auctions'},
            {'value': 'full', 'label': 'Full Synchronization'}
        ]
        return context

    def post(self, request, *args, **kwargs):
        try:
            sync_type = request.POST.get('sync_type', '')
            
            if sync_type == 'ended':
                sync_ended_auctions()
                message = 'Ended auctions synchronized successfully.'
            elif sync_type == 'active':
                sync_active_auctions()
                message = 'Active auctions synchronized successfully.'
            elif sync_type == 'full':
                sync_ended_auctions()
                sync_active_auctions()
                message = 'Full auction synchronization completed successfully.'
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Invalid synchronization type.'
                }, status=400)
            
            return JsonResponse({
                'status': 'success', 
                'message': message
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)