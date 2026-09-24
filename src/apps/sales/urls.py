from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "sales"

urlpatterns = [
    path('', views.sales_list, name="list_sales"),
    path('new/', views.new_sale, name="new_sale"),
    path('<int:sale_id>/items/add/', views.add_sale_item, name="add_sale_item"),
    path('products/search/', views.search_sale_products, name="search_sale_products"),
    path('<int:sale_id>/items/add-manual/', views.add_sale_product_manually, name="add_sale_product_manually"),
    path('<int:sale_id>/items/<int:item_id>/quantity/', views.update_sale_item_quantity, name="update_sale_item_quantity"),
    path('<int:sale_id>/summary/', views.update_sale_summary_view, name="update_sale_summary"),
    path('<int:sale_id>/summary', views.update_sale_summary_view),
    path('<int:sale_id>', views.sale_detail),
    path('<int:sale_id>/', views.sale_detail, name="sale_detail"),
]
