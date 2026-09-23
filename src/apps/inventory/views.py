from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.inventory.services import get_inventory_list_context


def inventory_list(request):
    context = get_inventory_list_context(request)

    context.update({
        "title": "Estoque",
        "page": "inventory",
    })

    return render(request, "inventory/pages/inventory.html", context)
