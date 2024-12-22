from django.db import models

class AuctionItem(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    uri = models.CharField(max_length=255)
    mini_photo = models.ImageField(upload_to='auction_photos/', blank=True, null=True, default='default_image.png')
    status = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True)
    currency = models.CharField(max_length=255)


    def __str__(self):
        return self.name

class Bid(models.Model):
    auction_item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    user = models.CharField(max_length=255)
    offer = models.FloatField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user} - {self.offer}"