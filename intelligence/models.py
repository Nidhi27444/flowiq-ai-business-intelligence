from django.conf import settings
from django.db import models

class Dataset(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=160)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    record_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name

class Sale(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='sales')
    order_date = models.DateField()
    customer = models.CharField(max_length=150)
    product = models.CharField(max_length=150)
    country = models.CharField(max_length=80)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    revenue = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=['dataset', 'order_date'], name='sale_dataset_date_idx')]
