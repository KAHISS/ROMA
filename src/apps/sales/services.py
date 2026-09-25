from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, Sum, Value
from django.db.models.functions import Coalesce
from django.db.models import Q
from apps.sales.filters import SaleFilter
from apps.inventory.models import Product
from apps.inventory.services import format_brl
from apps.sales.models import Sale, SaleItem
from utils.pagination import make_pagination


class InsufficientStockError(Exception):
    """Raised when a sale would consume more units than are available."""


def get_sales_list_context(request, per_page=10):

    queryset = Sale.objects.all().order_by("-created_at")

    sale_filter = SaleFilter(request.GET, queryset=queryset)
    filtered_sales = sale_filter.qs

    sales, pagination_range = make_pagination(request, filtered_sales, per_page)

    monetary_field = DecimalField(max_digits=20, decimal_places=2)
    total_price_expr = ExpressionWrapper(Sum("total_price"), output_field=monetary_field)

    aggregates = filtered_sales.aggregate(
        total_sales=Coalesce(total_price_expr, Value(0), output_field=monetary_field),
        total_paid_sales=Coalesce(Count("id", filter=Q(status=Sale.Status.PAID)), Value(0)),
        total_pending_sales=Coalesce(Count("id", filter=Q(status=Sale.Status.PENDING)), Value(0)),
        total_paid_amount=Coalesce(
            Sum("total_price", filter=Q(status=Sale.Status.PAID)),
            Value(0),
            output_field=monetary_field,
        ),
        total_pending_amount=Coalesce(
            Sum("total_price", filter=Q(status=Sale.Status.PENDING)),
            Value(0),
            output_field=monetary_field,
        ),
    )

    get_copy = request.GET.copy()
    if "page" in get_copy:
        del get_copy["page"]
    additional_url_query = "&" + get_copy.urlencode() if get_copy else ""

    return {
        "filter": sale_filter,
        "pagination_range": pagination_range,
        "objects": sales,
        "sales": sales,
        "additional_url_query": additional_url_query,
        "total_sales": format_brl(aggregates["total_sales"]),
        "total_paid_sales": aggregates["total_paid_sales"],
        "total_pending_sales": aggregates["total_pending_sales"],
        "total_paid_amount": format_brl(aggregates["total_paid_amount"]),
        "total_pending_amount": format_brl(aggregates["total_pending_amount"]),
    }


def create_sale(form):
    """Validate and persist a ``Sale`` submitted through ``SaleForm``.
    Returns the saved instance or ``None`` if the form is invalid.
    """
    if not form.is_valid():
        return None
    return form.save()


def update_sale(sale_id, form):
    """Validate and update an existing ``Sale`` instance.
    Returns the updated sale or ``None`` if the form is invalid.
    """
    if not form.is_valid():
        return None
    sale = Sale.objects.get(pk=sale_id)
    for field, value in form.cleaned_data.items():
        setattr(sale, field, value)
    sale.save()
    return sale


@transaction.atomic
def update_sale_summary(sale_id, form):
    """Validate and persist the editable sale summary fields."""
    if not form.is_valid():
        return None

    sale = Sale.objects.select_for_update().get(pk=sale_id)
    for field, value in form.cleaned_data.items():
        setattr(sale, field, value)
    if sale.payment_method != Sale.PaymentMethod.CASH:
        sale.cash_received = 0
    sale.total_price = sale.subtotal - sale.discount + sale.freight
    sale.save(update_fields=[
        "client",
        "status",
        "payment_method",
        "discount",
        "freight",
        "cash_received",
        "total_price",
        "updated_at",
    ])
    return sale


def delete_sale(sale_id):
    """Delete a ``Sale`` by its primary key."""
    sale = Sale.objects.get(pk=sale_id)
    sale.delete()


def delete_zero_total_sales():
    """Remove abandoned sales that have no value before starting a new sale."""
    Sale.objects.filter(total_price=0).delete()


def _refresh_sale_totals(sale):
    items = sale.sale_items.all()
    sale.total_quantity = sum(item.quantity for item in items)
    sale.subtotal = sum(item.subtotal for item in items)
    sale.total_price = sale.subtotal - sale.discount + sale.freight
    sale.save(update_fields=["total_quantity", "subtotal", "total_price", "updated_at"])


def search_products_for_sale(query, limit=20):
    """Find products by description, brand, or barcode for manual sale entry."""
    query = query.strip()
    if not query:
        return Product.objects.none()

    return Product.objects.filter(
        Q(description__icontains=query)
        | Q(brand__icontains=query)
        | Q(barcode__icontains=query)
    ).order_by("description")[:limit]


def _add_product_instance_to_sale(sale_id, product):
    sale = Sale.objects.select_for_update().get(pk=sale_id)
    product = Product.objects.select_for_update().get(pk=product.pk)
    if product.quantity <= 0:
        raise InsufficientStockError

    product.quantity -= 1
    product.save(update_fields=["quantity", "updated_at"])

    sale_item, created = SaleItem.objects.get_or_create(
        sale=sale,
        product=product,
        defaults={"quantity": 1, "subtotal": product.price},
    )

    if not created:
        sale_item.quantity += 1
        sale_item.subtotal = product.price * sale_item.quantity
        sale_item.save(update_fields=["quantity", "subtotal", "updated_at"])

    _refresh_sale_totals(sale)
    return sale, sale_item


@transaction.atomic
def add_product_to_sale(sale_id, barcode):
    """Add one product unit to a sale and refresh its totals."""
    product = Product.objects.get(barcode=barcode)
    return _add_product_instance_to_sale(sale_id, product)


@transaction.atomic
def add_product_by_id_to_sale(sale_id, product_id):
    """Add one product selected manually to a sale."""
    product = Product.objects.get(pk=product_id)
    return _add_product_instance_to_sale(sale_id, product)


@transaction.atomic
def change_sale_item_quantity(sale_id, item_id, delta):
    """Change an item's quantity and remove it when the quantity reaches zero."""
    sale = Sale.objects.select_for_update().get(pk=sale_id)
    sale_item = SaleItem.objects.select_for_update().get(pk=item_id, sale=sale)
    product = Product.objects.select_for_update().get(pk=sale_item.product_id)

    if delta == 1:
        if product.quantity <= 0:
            raise InsufficientStockError
        product.quantity -= 1
    else:
        product.quantity += 1
    product.save(update_fields=["quantity", "updated_at"])

    sale_item.quantity += delta

    if sale_item.quantity <= 0:
        sale_item.delete()
        sale_item = None
    else:
        sale_item.subtotal = sale_item.product.price * sale_item.quantity
        sale_item.save(update_fields=["quantity", "subtotal", "updated_at"])

    _refresh_sale_totals(sale)
    return sale, sale_item
