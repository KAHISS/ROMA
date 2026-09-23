import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method="custom_search",
        label="Buscar",
    )

    is_active = django_filters.ChoiceFilter(
        choices=[
            ("true", "Ativos"),
            ("false", "Inativos"),
        ],
        method="filter_is_active",
        label="Status",
    )

    role = django_filters.ChoiceFilter(
        choices=[
            ("staff", "Administrador"),
            ("user", "Usuário"),
        ],
        method="filter_role",
        label="Tipo de acesso",
    )

    class Meta:
        model = User
        fields = ["is_active", "role"]

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(username__icontains=value)
            | Q(email__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        return queryset.filter(is_active=value == "true")

    def filter_role(self, queryset, name, value):
        if value == "staff":
            return queryset.filter(is_staff=True)

        if value == "user":
            return queryset.filter(is_staff=False)

        return queryset