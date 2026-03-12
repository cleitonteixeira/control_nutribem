from django.urls import path

from . import views

app_name = 'control'

urlpatterns = [
    path('',views.home, name="index"),
    path('unidades/', views.UnidadesView, name="unidades"),
    path('unidade/nova/', views.cadastrar_unidade, name='cadastrar_unidade'),
    path('unidade/<int:pk>/editar/', views.editar_unidade, name='editar_unidade'),
    path('equipamentos/', views.EquipamentosView, name="equipamentos"),
    path('equipamento/novo/', views.cadastrar_equipamento, name='cadastrar_equipamento'),
    path('equipamento/<int:pk>/transferir/', views.transferir_equipamento, name='transferir_equipamento'),
    path('equipamento/<int:pk>/editar/', views.editar_equipamento, name='editar_equipamento'),
    path('equipamento/load-tipos/', views.load_tipos, name='ajax_load_tipos'),
]