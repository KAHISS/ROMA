import django_filters
from django.db.models import Q
from .models import Sale


class SaleFilter(django_filters.FilterSet):
    # Busca por cliente, vendedor ou ID da venda
    search = django_filters.CharFilter(
        method="custom_search",
        label="Buscar",
    )

    # Filtro por status da venda (pago/pendente)
    status = django_filters.ChoiceFilter(
        choices=Sale.Status.choices,
        method="filter_status",
        label="Status",
    )

    # Filtro por método de pagamento
    payment_method = django_filters.ChoiceFilter(
        choices=Sale.PaymentMethod.choices,
        method="filter_payment_method",
        label="Método de pagamento",
    )

    # Filtro por intervalo de datas de criação
    created_at = django_filters.DateFromToRangeFilter(
        field_name="created_at",
        label="Data da venda",
    )

    class Meta:
        model = Sale
        fields = ["status", "payment_method", "created_at"]

    def custom_search(self, queryset, name, value):
        """
        Procura nas colunas de busca:
        - client (nome do cliente)
        - seller__username (nome de usuário do vendedor)
        - id (número da venda)
        """
        return queryset.filter(
            Q(client__icontains=value)
            | Q(seller__username__icontains=value)
            | Q(id__icontains=value)
        )

    def filter_status(self, queryset, name, value):
        return queryset.filter(status=value)

    def filter_payment_method(self, queryset, name, value):
        return queryset.filter(payment_method=value)