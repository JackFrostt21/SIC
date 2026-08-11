from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    # позже:
    # path('<slug:project_slug>/', views.project_detail, name='project_detail'),
    # path('<slug:project_slug>/<slug:page_slug>/', views.page_detail, name='page_detail'),
]