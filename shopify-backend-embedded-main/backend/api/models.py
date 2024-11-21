from django.db import models

class Shop(models.Model):
    domain = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    access_scopes = models.TextField()

    created_at = models.BigIntegerField()
    updated_at = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.domain}"


class Order(models.Model):
    order_id = models.BigIntegerField(unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3)
    current_subtotal_price = models.DecimalField(max_digits=10, decimal_places=3)

    created_at = models.BigIntegerField()

    def __str__(self):
        return f"order {self.order_id}"


class WebhookEvent(models.Model):
    event_id = models.CharField(unique=True)
    
    created_at = models.BigIntegerField()

    def __str__(self):
        return f"{self.event_id}"
