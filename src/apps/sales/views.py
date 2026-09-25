from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import environ

from apps.inventory.models import Product
from apps.sales.forms import SaleForm
from apps.sales.models import Sale, SaleItem
from apps.sales.services import (
    get_sales_list_context,
    create_sale,
    add_product_to_sale,
    add_product_by_id_to_sale,
    InsufficientStockError,
    change_sale_item_quantity,
    search_products_for_sale,
    update_sale_summary,
    update_sale,
    delete_sale,
)

env = environ.Env()

PER_PAGE = env.int("PER_PAGE", default=12)


@login_required
def sales_list(request):
    if request.method == "POST" and request.POST.get("action") == "delete":
        sale_id = request.POST.get("sale_id")
        try:
            delete_sale(sale_id)
        except Sale.DoesNotExist:
            pass
        return redirect("sales:list_sales")

    context = get_sales_list_context(request, PER_PAGE)
    context.update({
        "title": "Vendas",
        "page": "sales",
    })

    return render(request, "sales/pages/sales.html", context)


@login_required
def new_sale(request):
    form = SaleForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        sale = form.save(commit=False)
        sale.seller = request.user
        sale.save()
        return render(request, "sales/pages/sale.html", {"sale": sale})

    if request.method == "POST":
        return JsonResponse({"error": "Dados da venda inválidos."}, status=400)

    sale = Sale.objects.filter(
        seller=request.user,
        total_price=0,
    ).order_by("-created_at").first()
    if sale is None:
        sale = Sale.objects.create(seller=request.user)
    return render(request, "sales/pages/sale.html", {"sale": sale, "form": form})


@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale)
        updated_sale = update_sale_summary(sale_id, form)
        if updated_sale is None:
            error = next(iter(form.errors.values()))[0]
            return JsonResponse({"error": error}, status=400)

        return JsonResponse({
            "sale": {
                "subtotal": f"R$ {updated_sale.subtotal:.2f}".replace(".", ","),
                "total_price": f"R$ {updated_sale.total_price:.2f}".replace(".", ","),
                "discount": f"R$ {updated_sale.discount:.2f}".replace(".", ","),
                "freight": f"R$ {updated_sale.freight:.2f}".replace(".", ","),
            },
        })

    sale = Sale.objects.prefetch_related("sale_items__product").get(pk=sale_id)
    return render(request, "sales/pages/sale.html", {"sale": sale})


@login_required
def add_sale_item(request, sale_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    barcode = request.POST.get("barcode", "").strip()
    if not barcode:
        return JsonResponse({"error": "Informe o código de barras."}, status=400)

    try:
        sale, sale_item = add_product_to_sale(sale_id, barcode)
    except Sale.DoesNotExist:
        return JsonResponse({"error": "Venda não encontrada."}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Produto não encontrado."}, status=404)
    except InsufficientStockError:
        return JsonResponse({"error": "Produto sem estoque disponível."}, status=400)

    return JsonResponse({
        "item": {
            "id": sale_item.id,
            "description": sale_item.product.description,
            "brand": sale_item.product.brand or "",
            "barcode": sale_item.product.barcode,
            "quantity": sale_item.quantity,
            "quantity_url": reverse("sales:update_sale_item_quantity", args=[sale.pk, sale_item.pk]),
            "subtotal": f"R$ {sale_item.subtotal:.2f}".replace(".", ","),
        },
        "sale": {
            "total_quantity": sale.total_quantity,
            "subtotal": f"R$ {sale.subtotal:.2f}".replace(".", ","),
            "total_price": f"R$ {sale.total_price:.2f}".replace(".", ","),
        },
    })


@login_required
def search_sale_products(request):
    query = request.GET.get("q", "")
    products = search_products_for_sale(query)
    return JsonResponse({
        "products": [
            {
                "id": product.id,
                "description": product.description,
                "brand": product.brand or "",
                "barcode": product.barcode,
                "price": f"R$ {product.price:.2f}".replace(".", ","),
                "quantity": product.quantity,
            }
            for product in products
        ],
    })


@login_required
def add_sale_product_manually(request, sale_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    try:
        sale, sale_item = add_product_by_id_to_sale(
            sale_id,
            request.POST.get("product_id"),
        )
    except InsufficientStockError:
        return JsonResponse({"error": "Produto sem estoque disponível."}, status=400)
    except (Sale.DoesNotExist, Product.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"error": "Produto ou venda não encontrado."}, status=404)

    return JsonResponse({
        "item": {
            "id": sale_item.id,
            "description": sale_item.product.description,
            "brand": sale_item.product.brand or "",
            "barcode": sale_item.product.barcode,
            "quantity": sale_item.quantity,
            "quantity_url": reverse("sales:update_sale_item_quantity", args=[sale.pk, sale_item.pk]),
            "subtotal": f"R$ {sale_item.subtotal:.2f}".replace(".", ","),
        },
        "sale": {
            "total_quantity": sale.total_quantity,
            "subtotal": f"R$ {sale.subtotal:.2f}".replace(".", ","),
            "total_price": f"R$ {sale.total_price:.2f}".replace(".", ","),
        },
    })


@login_required
def update_sale_item_quantity(request, sale_id, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    try:
        delta = int(request.POST.get("delta", "0"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Quantidade inválida."}, status=400)

    if delta not in (-1, 1):
        return JsonResponse({"error": "A quantidade deve variar em uma unidade."}, status=400)

    try:
        sale, sale_item = change_sale_item_quantity(sale_id, item_id, delta)
    except InsufficientStockError:
        return JsonResponse({"error": "Produto sem estoque disponível."}, status=400)
    except (Sale.DoesNotExist, SaleItem.DoesNotExist):
        return JsonResponse({"error": "Item da venda não encontrado."}, status=404)

    item_data = None
    if sale_item is not None:
        item_data = {
            "quantity": sale_item.quantity,
            "subtotal": f"R$ {sale_item.subtotal:.2f}".replace(".", ","),
        }

    return JsonResponse({
        "item": item_data,
        "sale": {
            "total_quantity": sale.total_quantity,
            "subtotal": f"R$ {sale.subtotal:.2f}".replace(".", ","),
            "total_price": f"R$ {sale.total_price:.2f}".replace(".", ","),
        },
    })


@login_required
def update_sale_summary_view(request, sale_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    sale = get_object_or_404(Sale, pk=sale_id)
    form = SaleForm(request.POST, instance=sale)
    updated_sale = update_sale_summary(sale_id, form)

    if updated_sale is None:
        error = next(iter(form.errors.values()))[0]
        return JsonResponse({"error": error}, status=400)

    return JsonResponse({
        "sale": {
            "subtotal": f"R$ {updated_sale.subtotal:.2f}".replace(".", ","),
            "total_price": f"R$ {updated_sale.total_price:.2f}".replace(".", ","),
            "discount": f"R$ {updated_sale.discount:.2f}".replace(".", ","),
            "freight": f"R$ {updated_sale.freight:.2f}".replace(".", ","),
        },
    })
