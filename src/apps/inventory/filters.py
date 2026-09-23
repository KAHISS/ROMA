import django_filters
from django.db.models import Q
from .models import Product

class ProductFilter(django_filters.FilterSet):
    # Campo de busca customizado que procura tanto no código de barras quanto na descrição
    search = django_filters.CharFilter(
        method='custom_search',
        label='Buscar'
    )

    # Filtro por marca
    brand = django_filters.CharFilter(
        field_name='brand',
        lookup_expr='icontains',
        label='Marca'
    )

    class Meta:
        model = Product
        fields = ['brand']

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(description__icontains=value) |
            Q(barcode__icontains=value)
        )

