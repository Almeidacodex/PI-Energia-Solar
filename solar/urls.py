from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculadora, name='calculadora'),
    path('calcular/', views.calcular, name='calcular'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('orcamento/<int:orcamento_id>/pdf/', views.download_pdf, name='download_pdf'),
]