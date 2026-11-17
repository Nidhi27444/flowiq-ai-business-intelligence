from django.contrib import admin
from .models import Dataset, Sale
@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'record_count', 'uploaded_at')
    search_fields = ('name', 'owner__username')
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'order_date', 'customer', 'product', 'revenue')
    list_filter = ('dataset', 'country')
