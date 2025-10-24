from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'), 

    # Nuevas URLs para Fijos
    path('recurring/', views.manage_recurring, name='manage_recurring'),
    path('recurring/delete/<int:pk>/', views.delete_recurring, name='delete_recurring'),

    # Nuevas URLs para Tarjetas
    path('cards/', views.manage_cards, name='manage_cards'),
    path('cards/delete/<int:pk>/', views.delete_card, name='delete_card'),
]