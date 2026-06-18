"""
Lógica de negócio do Bloco de Notas.

De propósito, este módulo NÃO sabe nada sobre Django, HTTP ou sessão.
Recebe e devolve listas de dicionários puros. Essa separação é o que
torna a lógica fácil de testar com pytest puro, sem precisar de um
cliente HTTP ou de banco de dados — é o ponto principal a destacar na
aula de testes/CI.
"""

from datetime import datetime
from typing import List, Optional

TITULO_MAX_LEN = 80
CONTEUDO_MAX_LEN = 2000


class NotaInvalida(ValueError):
    """Erro de validação de uma nota (título/conteúdo inválidos ou nota não encontrada)."""


def validar_nota(titulo: str, conteudo: str) -> None:
    """Levanta NotaInvalida se título ou conteúdo não passarem nas regras de negócio."""
    titulo = (titulo or "").strip()
    conteudo = (conteudo or "").strip()

    if not titulo:
        raise NotaInvalida("O título não pode estar vazio.")
    if len(titulo) > TITULO_MAX_LEN:
        raise NotaInvalida(
            f"O título não pode ter mais de {TITULO_MAX_LEN} caracteres."
        )
    if not conteudo:
        raise NotaInvalida("O conteúdo não pode estar vazio.")
    if len(conteudo) > CONTEUDO_MAX_LEN:
        raise NotaInvalida(
            f"O conteúdo não pode ter mais de {CONTEUDO_MAX_LEN} caracteres."
        )


def proximo_id(notas: List[dict]) -> int:
    """Calcula o próximo id disponível em uma lista de notas."""
    if not notas:
        return 1
    return max(n["id"] for n in notas) + 1


def adicionar_nota(notas: List[dict], titulo: str, conteudo: str) -> List[dict]:
    """Retorna uma NOVA lista de notas com a nota adicionada (não modifica a lista recebida)."""
    validar_nota(titulo, conteudo)
    agora = datetime.now().isoformat()
    nova = {
        "id": proximo_id(notas),
        "titulo": titulo.strip(),
        "conteudo": conteudo.strip(),
        "criada_em": agora,
        "atualizada_em": agora,
    }
    return notas + [nova]


def editar_nota(
    notas: List[dict], nota_id: int, titulo: str, conteudo: str
) -> List[dict]:
    """Retorna uma nova lista com a nota `nota_id` atualizada."""
    validar_nota(titulo, conteudo)
    encontrada = False
    novas = []
    for nota in notas:
        if nota["id"] == nota_id:
            encontrada = True
            nota = {
                **nota,
                "titulo": titulo.strip(),
                "conteudo": conteudo.strip(),
                "atualizada_em": datetime.now().isoformat(),
            }
        novas.append(nota)
    if not encontrada:
        raise NotaInvalida(f"Nota com id {nota_id} não encontrada.")
    return novas


def remover_nota(notas: List[dict], nota_id: int) -> List[dict]:
    """Retorna uma nova lista sem a nota `nota_id`."""
    novas = [n for n in notas if n["id"] != nota_id]
    if len(novas) == len(notas):
        raise NotaInvalida(f"Nota com id {nota_id} não encontrada.")
    return novas


def buscar_notas(notas: List[dict], termo: Optional[str]) -> List[dict]:
    """Filtra notas cujo título ou conteúdo contenham `termo` (case-insensitive)."""
    if not termo:
        return list(notas)
    termo_lower = termo.strip().lower()
    return [
        n
        for n in notas
        if termo_lower in n["titulo"].lower() or termo_lower in n["conteudo"].lower()
    ]


def ordenar_por_atualizacao(notas: List[dict]) -> List[dict]:
    """Ordena notas da mais recentemente atualizada para a mais antiga."""
    return sorted(notas, key=lambda n: n["atualizada_em"], reverse=True)
