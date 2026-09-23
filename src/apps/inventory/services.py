from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.inventory.filters import ProductFilter
from apps.inventory.models import Product
from utils.pagination import make_pagination


def format_brl(value):
    """Format a decimal value as Brazilian Real currency."""
    formatted_value = f"{value:,.2f}"
    formatted_value = formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted_value}"


def get_inventory_list_context(request, per_page=10):
    queryset = Product.objects.all().order_by("-created_at")

    product_filter = ProductFilter(request.GET, queryset=queryset)
    filtered_products = product_filter.qs

    monetary_field = DecimalField(max_digits=20, decimal_places=2)
    inventory_cost = ExpressionWrapper(
        F("cust") * F("quantity"),
        output_field=monetary_field,
    )
    sales_potential = ExpressionWrapper(
        F("price") * F("quantity"),
        output_field=monetary_field,
    )

    totals = filtered_products.aggregate(
        total_units=Coalesce(Sum("quantity"), Value(0)),
        total_inventory_cost=Coalesce(
            Sum(inventory_cost),
            Value(Decimal("0.00")),
            output_field=monetary_field,
        ),
        total_sales_potential=Coalesce(
            Sum(sales_potential),
            Value(Decimal("0.00")),
            output_field=monetary_field,
        ),
    )

    products, pagination_range = make_pagination(
        request, filtered_products, per_page
    )

    get_copy = request.GET.copy()
    if "page" in get_copy:
        del get_copy["page"]
    additional_url_query = "&" + get_copy.urlencode() if get_copy else ""

    return {
        "filter": product_filter,
        "pagination_range": pagination_range,
        "objects": products,
        "products": products,
        "additional_url_query": additional_url_query,
        "total_products": filtered_products.count(),
        "total_units": totals["total_units"],
        "total_inventory_cost": format_brl(totals["total_inventory_cost"]),
        "total_sales_potential": format_brl(totals["total_sales_potential"]),
    }


def create_product(form):
    if not form.is_valid():
        return None

    return form.save()


def update_product(product_id, form):
    """Validate and update an existing product through ProductForm."""
    if not form.is_valid():
        return None

    product = Product.objects.get(pk=product_id)

    for field, value in form.cleaned_data.items():
        setattr(product, field, value)

    product.save()
    return product


def delete_product(product_id):
    """Delete a product by its primary key."""
    product = Product.objects.get(pk=product_id)
    product.delete()
