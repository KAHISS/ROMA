from django.contrib import admin

from apps.inventory.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'barcode',
        'description',
        'brand',
        'cust',
        'price',
        'quantity',
        'min_quantity',
        'status_label',
        'created_at',
        'updated_at',
    )
    list_display_links = ('id', 'description')
    search_fields = ('barcode', 'description', 'brand')
    list_filter = ('brand', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'status_label')
    list_per_page = 25

    fieldsets = (
        ('Identificação', {
            'fields': ('barcode', 'description', 'brand')
        }),
        ('Estoque e Preço', {
            'fields': ('cust', 'price', 'quantity', 'min_quantity', 'status_label')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
