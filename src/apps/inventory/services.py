from decimal import Decimal

from django.db.models import Case, DecimalField, ExpressionWrapper, F, Sum, Value, When
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
    monetary_field = DecimalField(max_digits=20, decimal_places=2)
    total_profit = ExpressionWrapper(
        (F("price") - F("cust")) * F("quantity"),
        output_field=monetary_field,
    )
    percentage_field = DecimalField(max_digits=8, decimal_places=2)
    product_profit_percentage = Case(
        When(
            price__gt=0,
            then=ExpressionWrapper(
                (F("price") - F("cust")) * Value(Decimal("100.00")) / F("price"),
                output_field=percentage_field,
            ),
        ),
        default=Value(Decimal("0.00"), output_field=percentage_field),
        output_field=percentage_field,
    )
    filtered_products = product_filter.qs.annotate(
        total_profit=total_profit,
        profit_percentage=product_profit_percentage,
    )

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
        total_profit_potential=Coalesce(
            Sum(total_profit),
            Value(Decimal("0.00")),
            output_field=monetary_field,
        ),
    )
    total_profit_percentage = Decimal("0.00")
    if totals["total_sales_potential"] > 0:
        total_profit_percentage = (
            totals["total_profit_potential"] * Decimal("100.00")
            / totals["total_sales_potential"]
        ).quantize(Decimal("0.01"))

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
        "total_profit_potential": format_brl(totals["total_profit_potential"]),
        "total_profit_percentage": total_profit_percentage,
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
