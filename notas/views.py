import os

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from . import services

SESSION_KEY = "notas"


def _get_notas(request):
    return request.session.get(SESSION_KEY, [])


def _set_notas(request, notas):
    request.session[SESSION_KEY] = notas
    request.session.modified = True


def lista_notas(request):
    termo = request.GET.get("q", "").strip()
    notas = _get_notas(request)
    notas_filtradas = services.buscar_notas(notas, termo)
    notas_ordenadas = services.ordenar_por_atualizacao(notas_filtradas)
    contexto = {
        "notas": notas_ordenadas,
        "termo": termo,
        "total": len(notas),
    }
    return render(request, "notas/lista.html", contexto)


@require_http_methods(["POST"])
def criar_nota(request):
    notas = _get_notas(request)
    try:
        notas = services.adicionar_nota(
            notas, request.POST.get("titulo", ""), request.POST.get("conteudo", "")
        )
        _set_notas(request, notas)
        messages.success(request, "Nota criada com sucesso!")
    except services.NotaInvalida as erro:
        messages.error(request, str(erro))
    return redirect("notas:lista")


def editar_nota_view(request, nota_id):
    notas = _get_notas(request)
    nota = next((n for n in notas if n["id"] == nota_id), None)
    if nota is None:
        messages.error(request, "Nota não encontrada.")
        return redirect("notas:lista")

    if request.method == "POST":
        try:
            notas = services.editar_nota(
                notas,
                nota_id,
                request.POST.get("titulo", ""),
                request.POST.get("conteudo", ""),
            )
            _set_notas(request, notas)
            messages.success(request, "Nota atualizada!")
            return redirect("notas:lista")
        except services.NotaInvalida as erro:
            messages.error(request, str(erro))

    return render(request, "notas/editar.html", {"nota": nota})


@require_http_methods(["POST"])
def remover_nota_view(request, nota_id):
    notas = _get_notas(request)
    try:
        notas = services.remover_nota(notas, nota_id)
        _set_notas(request, notas)
        messages.success(request, "Nota removida.")
    except services.NotaInvalida as erro:
        messages.error(request, str(erro))
    return redirect("notas:lista")


def healthz(request):
    """Endpoint simples de verificação de saúde, útil para o Cloud Run."""
    return JsonResponse(
        {"status": "ok", "versao": os.environ.get("GIT_SHA", "dev")[:7]}
    )
