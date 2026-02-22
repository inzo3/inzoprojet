from django.urls import path
from . import views

app_name = 'annonces'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('annonce/<int:pk>/', views.annonce_detail_view, name='annonce_detail'),
    path('recherche/', views.recherche_view, name='recherche'),
    path('creer/', views.annonce_create_view, name='annonce_create'),
]
