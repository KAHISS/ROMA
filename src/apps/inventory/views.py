import environ

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.inventory.forms import ProductForm
from apps.inventory.models import Product
from apps.inventory.services import (
    create_product,
    delete_product,
    get_inventory_list_context,
    update_product,
)

env = environ.Env()

PER_PAGE = env.int("PER_PAGE", default=12)


@login_required
def inventory_list(request):
    form = ProductForm()

    if request.method == "POST":
        action = request.POST.get("action")
        product_id = request.POST.get("product_id")

        if action == "delete":
            try:
                delete_product(product_id)
                return redirect("inventory:list_inventory")
            except Product.DoesNotExist:
                form.add_error(None, "O produto selecionado não foi encontrado.")
        else:
            try:
                if product_id:
                    product_instance = Product.objects.get(pk=product_id)
                    form = ProductForm(request.POST, instance=product_instance)
                    product = update_product(product_id, form)
                else:
                    form = ProductForm(request.POST)
                    product = create_product(form)
            except Product.DoesNotExist:
                form = ProductForm(request.POST)
                form.add_error(None, "O produto selecionado não foi encontrado.")
                product = None

            if product is not None:
                return redirect("inventory:list_inventory")

    context = get_inventory_list_context(request, PER_PAGE)
    context.update({
        "form": form,
        "title": "Estoque",
        "page": "inventory",
    })

    return render(request, "inventory/pages/inventory.html", context)
