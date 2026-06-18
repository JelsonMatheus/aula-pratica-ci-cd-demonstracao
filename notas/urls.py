from django.urls import path

from . import views

app_name = "notas"

urlpatterns = [
    path("", views.lista_notas, name="lista"),
    path("nova/", views.criar_nota, name="criar"),
    path("<int:nota_id>/editar/", views.editar_nota_view, name="editar"),
    path("<int:nota_id>/remover/", views.remover_nota_view, name="remover"),
]
