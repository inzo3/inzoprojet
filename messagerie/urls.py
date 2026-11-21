from django.urls import path
from . import views

app_name = 'messagerie'

urlpatterns = [
    path('favori/ajouter/<int:annonce_id>/', views.ajouter_favori, name='ajouter_favori'),
    path('favori/retirer/<int:annonce_id>/', views.retirer_favori, name='retirer_favori'),
    path('messages/recus/', views.messages_recus, name='messages_recus'),
    path('messages/<int:pk>/', views.detail_message, name='detail_message'),
    path('messages/<int:pk>/supprimer/', views.supprimer_conversation, name='supprimer_conversation'),
    path('message/envoyer/<int:annonce_id>/', views.envoyer_message, name='envoyer_message'),
]
