import os
import logging
import requests
import re

from urllib.parse import urlparse
from django.core.files.base import ContentFile
from pathlib import Path
from auction.models import AuctionItem, Bid

logger = logging.getLogger(__name__)

GOODS_URL = "https://subastas.justiciacordoba.gob.ar/api/good_search/"
PUBLIC_OFFER_URL = "https://subastas.justiciacordoba.gob.ar/api/public_offer/"

def download_and_save_image(url, item_id):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.jpg'
            
        filename = f'auction_{item_id}{ext}'
        image_content = ContentFile(response.content)
        
        return filename, image_content
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return None, None

def sync_items(status):
    try:
        logger.info("Starting items synchronization...")
        goods_response = requests.get(GOODS_URL + f"?status={status}&limit=50000&cat_id=20")
        goods_response.raise_for_status()
        goods_data = goods_response.json().get('results', [])
        
        for item in goods_data:
            try:
                image_filename, image_content = None, None
                if item['mini_photo']:
                    image_filename, image_content = download_and_save_image(item['mini_photo'], item['id'])
                
                defaults = {
                    'name': item['name'],
                    'price': item['price'],
                    'start_date': item['start_date'],
                    'end_date': item['end_date'],
                    'uri': item['uri'],
                    'status': status,
                    'category': item['category']['name'],
                    'currency': item['currency']['code']
                }
                
                auction_item = AuctionItem.objects.filter(id=item['id']).first()
                
                if auction_item:
                    for key, value in defaults.items():
                        setattr(auction_item, key, value)
                    
                    if image_filename and image_content:
                        if auction_item.mini_photo:
                            try:
                                old_path = Path(auction_item.mini_photo.path)
                                if old_path.exists():
                                    old_path.unlink()
                            except Exception as e:
                                logger.error(f"Failed to delete old image for item {item['id']}: {e}")
                        
                        auction_item.mini_photo.save(image_filename, image_content, save=False)
                    
                    auction_item.save()
                    logger.info(f"Updated AuctionItem: {auction_item.name} (ID: {auction_item.id})")
                else:
                    if image_filename and image_content:
                        auction_item = AuctionItem(id=item['id'], **defaults)
                        auction_item.mini_photo.save(image_filename, image_content, save=False)
                        auction_item.save()
                    else:
                        auction_item = AuctionItem.objects.create(id=item['id'], **defaults)
                    logger.info(f"Added new AuctionItem: {auction_item.name} (ID: {auction_item.id})")
                
            except Exception as e:
                logger.error(f"An error occurred while processing AuctionItem ID {item['id']}: {e}")
                
        logger.info("Items synchronization completed.")
    except requests.RequestException as e:
        logger.error(f"Failed to fetch goods data: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during items synchronization: {e}")


def sync_bids(status):
    try:
        logger.info("Starting bids synchronization...")
        auction_items = AuctionItem.objects.filter(status=status)
        for auction_item in auction_items:
            try:
                bids_url = f"{PUBLIC_OFFER_URL}?limit=100000&product_id={auction_item.id}"
                bids_response = requests.get(bids_url)
                bids_response.raise_for_status()
                bids_data = bids_response.json().get('results', [])

                for bid in bids_data:
                    Bid.objects.update_or_create(
                        auction_item=auction_item,
                        user=bid['user'],
                        offer=bid['offer'],
                        date=bid['date']
                    )
                logger.info(f"Processed {len(bids_data)} bids for AuctionItem ID: {auction_item.id}")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch bids for AuctionItem ID {auction_item.id}: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing bids for AuctionItem ID {auction_item.id}: {e}")

        logger.info("Bids synchronization completed.")

    except requests.RequestException as e:
        logger.error(f"Failed to fetch goods data for bids synchronization: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during bids synchronization: {e}")


def sync_ended_auctions():
    try:
        logger.info("Starting full synchronization...")
        
        sync_items("ended")
        sync_bids("ended")

        logger.info("Full synchronization completed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during full synchronization: {e}")

def sync_active_auctions():
    try:
        logger.info("Starting active auctions synchronization...")
        
        sync_items("active")
        sync_bids("active")

        logger.info("Active auctions synchronization completed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during active auctions synchronization: {e}")

def extract_auction_id(url):
    """Extract auction ID from URL using regex"""
    pattern = r'/product/cba/(\d+)/'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def sync_single_auction(auction_id):
    """Sync a single auction from the API"""
    api_url = f"https://subastas.justiciacordoba.gob.ar/api/public_good/{auction_id}/"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        item = response.json()
        
        image_filename, image_content = None, None
        if item['mini_photo']:
            image_filename, image_content = download_and_save_image(item['mini_photo'], item['id'])

        if item['status'] != 'Terminado':
            status = 'active'
        else:
            status = 'ended'
        
        defaults = {
            'name': item['name'],
            'price': item['price'],
            'start_date': item['start_date'],
            'end_date': item['end_date'],
            'uri': item['uri'],
            'status': status,
            'category': str(item.get('cat_id')),
            'currency': item['currency']['code']
        }
        
        auction_item = AuctionItem.objects.filter(id=item['id']).first()
        
        if auction_item:
            for key, value in defaults.items():
                setattr(auction_item, key, value)
            
            if image_filename and image_content:
                if auction_item.mini_photo:
                    try:
                        old_path = Path(auction_item.mini_photo.path)
                        if old_path.exists():
                            old_path.unlink()
                    except Exception as e:
                        logger.error(f"Failed to delete old image for item {item['id']}: {e}")
                auction_item.mini_photo.save(image_filename, image_content, save=False)
            
            auction_item.save()
        else:
            if image_filename and image_content:
                auction_item = AuctionItem(id=item['id'], **defaults)
                auction_item.mini_photo.save(image_filename, image_content, save=False)
                auction_item.save()
            else:
                auction_item = AuctionItem.objects.create(id=item['id'], **defaults)
        
        return auction_item.id
        
    except Exception as e:
        logger.error(f"Failed to sync auction {auction_id}: {e}")
        raise