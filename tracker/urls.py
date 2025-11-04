from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'), 

    # --- URLs de Transacciones ---
    path('transaction/add/', views.add_transaction, name='add_transaction'),
    path('category/add/', views.add_category, name='add_category'),
    
    # --- URLs de editar y borrar ---
    path('transaction/edit/<int:pk>/', views.transaction_update, name='transaction_update'),
    path('transaction/delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    
    # --- URL borrar categoria ---
    path('category/delete/<int:pk>/', views.category_delete, name='category_delete'),

    # --- URLs para Fijos ---
    path('recurring/', views.manage_recurring, name='manage_recurring'),
    path('recurring/delete/<int:pk>/', views.delete_recurring, name='delete_recurring'),

    # --- URLs para Tarjetas ---
    path('cards/', views.manage_cards, name='manage_cards'),
    path('cards/delete/<int:pk>/', views.delete_card, name='delete_card'),
    
    # --- URLS PARA CUENTAS ---
    path('accounts/manage/', views.manage_accounts, name='manage_accounts'),
    path('accounts/delete/<int:pk>/', views.delete_account, name='delete_account'),
    
    # --- URLS PARA PRESUPUESTOS ---
    path('budgets/', views.manage_budgets, name='manage_budgets'),
    path('budgets/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
]