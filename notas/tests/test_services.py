import pytest

from notas.services import (
    NotaInvalida,
    adicionar_nota,
    buscar_notas,
    editar_nota,
    ordenar_por_atualizacao,
    proximo_id,
    remover_nota,
    validar_nota,
)


def test_adicionar_nota_com_dados_validos():
    notas = adicionar_nota([], "Compras", "Comprar leite e pão")
    assert len(notas) == 1
    assert notas[0]["titulo"] == "Compras"
    assert notas[0]["id"] == 1


def test_adicionar_nota_atribui_ids_incrementais():
    notas = adicionar_nota([], "Primeira", "conteúdo 1")
    notas = adicionar_nota(notas, "Segunda", "conteúdo 2")
    assert [n["id"] for n in notas] == [1, 2]


@pytest.mark.parametrize(
    "titulo,conteudo",
    [
        ("", "algum conteúdo"),
        ("   ", "algum conteúdo"),
        ("Título ok", ""),
        ("Título ok", "   "),
    ],
)
def test_adicionar_nota_com_dados_invalidos_levanta_erro(titulo, conteudo):
    with pytest.raises(NotaInvalida):
        adicionar_nota([], titulo, conteudo)


def test_titulo_acima_do_limite_e_invalido():
    titulo_longo = "x" * 81
    with pytest.raises(NotaInvalida):
        validar_nota(titulo_longo, "conteúdo válido")


def test_conteudo_acima_do_limite_e_invalido():
    conteudo_longo = "x" * 2001
    with pytest.raises(NotaInvalida):
        validar_nota("Título válido", conteudo_longo)


def test_editar_nota_existente():
    notas = adicionar_nota([], "Original", "conteúdo original")
    nota_id = notas[0]["id"]
    notas = editar_nota(notas, nota_id, "Atualizado", "novo conteúdo")
    assert notas[0]["titulo"] == "Atualizado"
    assert notas[0]["conteudo"] == "novo conteúdo"


def test_editar_nota_inexistente_levanta_erro():
    with pytest.raises(NotaInvalida):
        editar_nota([], 999, "Título", "Conteúdo")


def test_remover_nota_existente():
    notas = adicionar_nota([], "Para remover", "conteúdo")
    nota_id = notas[0]["id"]
    notas = remover_nota(notas, nota_id)
    assert notas == []


def test_remover_nota_inexistente_levanta_erro():
    with pytest.raises(NotaInvalida):
        remover_nota([], 999)


def test_buscar_notas_por_titulo_e_case_insensitive():
    notas = adicionar_nota([], "Lista de Compras", "leite, pão, café")
    resultado = buscar_notas(notas, "compras")
    assert len(resultado) == 1


def test_buscar_notas_por_conteudo():
    notas = adicionar_nota([], "Lembrete", "ligar para o dentista")
    resultado = buscar_notas(notas, "dentista")
    assert len(resultado) == 1


def test_buscar_notas_sem_correspondencia_retorna_vazio():
    notas = adicionar_nota([], "Lembrete", "ligar para o dentista")
    resultado = buscar_notas(notas, "viagem")
    assert resultado == []


def test_buscar_notas_termo_vazio_retorna_todas():
    notas = adicionar_nota([], "Nota A", "conteúdo A")
    notas = adicionar_nota(notas, "Nota B", "conteúdo B")
    assert buscar_notas(notas, "") == notas


def test_ordenar_por_atualizacao_mais_recente_primeiro():
    notas = adicionar_nota([], "Primeira", "conteúdo")
    notas = adicionar_nota(notas, "Segunda", "conteúdo")
    notas = editar_nota(notas, 1, "Primeira editada", "conteúdo editado")
    ordenadas = ordenar_por_atualizacao(notas)
    assert ordenadas[0]["id"] == 1  # foi editada por último, deve vir primeiro


def test_proximo_id_em_lista_vazia():
    assert proximo_id([]) == 1
