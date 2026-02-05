from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    path('paiement/<int:annonce_id>/', views.paiement_view, name='paiement'),
]
