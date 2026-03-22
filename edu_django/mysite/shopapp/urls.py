from django.urls import path
from .views import shop_index, group_list, products_list

app_name = 'shopapp'

urlpatterns = [
    path('', shop_index, name='index'),
    path('groups/', group_list, name='groups_list'),
    path('products/', products_list, name='products_list'),
]