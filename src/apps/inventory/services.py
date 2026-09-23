from apps.inventory.models import Product
from apps.inventory.filters import ProductFilter
from utils.pagination import make_pagination

def get_inventory_list_context(request, per_page=10):
    """
    Função de serviço que executa a lógica de busca, filtro e paginação.
    """
    queryset = Product.objects.all().order_by('-created_at')

    # Instancia o filtro com os parâmetros da requisição
    product_filter = ProductFilter(request.GET, queryset=queryset)

    # Paginação
    products, pagination_range = make_pagination(
        request, product_filter.qs, per_page
    )

    # Constrói query params adicionais para manter filtros ao mudar de página
    get_copy = request.GET.copy()
    if 'page' in get_copy:
        del get_copy['page']
    additional_url_query = '&' + get_copy.urlencode() if get_copy else ''

    return {
        'filter': product_filter,
        'pagination_range': pagination_range,
        'objects': products,    # Usado no paginations.html
        'produtos': products,   # Usado na tabela de inventory.html
        'additional_url_query': additional_url_query,
    }

