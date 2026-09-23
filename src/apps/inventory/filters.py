import django_filters
from django.db.models import F, Q

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # Campo de busca customizado que procura tanto no código de barras quanto na descrição
    search = django_filters.CharFilter(
        method="custom_search",
        label="Buscar",
    )

    # Filtro por marca
    brand = django_filters.CharFilter(
        field_name="brand",
        lookup_expr="icontains",
        label="Marca",
    )

    stock_status = django_filters.ChoiceFilter(
        choices=[
            ("in_stock", "Em estoque"),
            ("low_stock", "Estoque baixo"),
            ("out_of_stock", "Esgotado"),
        ],
        method="filter_stock_status",
        label="Status do estoque",
    )

    class Meta:
        model = Product
        fields = ["brand", "stock_status"]

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(description__icontains=value) |
            Q(barcode__icontains=value)
        )

    def filter_stock_status(self, queryset, name, value):
        if value == "out_of_stock":
            return queryset.filter(quantity__lte=0)

        if value == "low_stock":
            return queryset.filter(
                quantity__gt=0,
                quantity__lte=F("min_quantity"),
            )

        if value == "in_stock":
            return queryset.filter(quantity__gt=F("min_quantity"))

        return queryset
