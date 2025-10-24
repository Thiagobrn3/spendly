from django.urls import path
from . import views

urlpatterns = [
    # Esta será nuestra página principal (el dashboard)
    path('', views.index, name='index'), 
]