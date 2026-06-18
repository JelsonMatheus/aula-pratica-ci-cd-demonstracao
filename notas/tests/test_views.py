def test_lista_vazia_mostra_mensagem(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Nenhuma nota encontrada" in response.content.decode()


def test_criar_nota_via_post_redireciona(client):
    response = client.post(
        "/nova/", {"titulo": "Teste", "conteudo": "Conteúdo de teste"}
    )
    assert response.status_code == 302


def test_criar_nota_aparece_na_lista(client):
    client.post(
        "/nova/", {"titulo": "Estudar Django", "conteudo": "Revisar views e testes"}
    )
    response = client.get("/")
    assert "Estudar Django" in response.content.decode()


def test_criar_nota_com_titulo_vazio_nao_adiciona(client):
    client.post("/nova/", {"titulo": "", "conteudo": "Conteúdo qualquer"})
    response = client.get("/")
    assert "Conteúdo qualquer" not in response.content.decode()


def test_buscar_via_querystring_filtra_resultado(client):
    client.post(
        "/nova/", {"titulo": "Reunião de equipe", "conteudo": "Pauta da sprint"}
    )
    client.post("/nova/", {"titulo": "Lista de compras", "conteudo": "Leite e pão"})
    response = client.get("/?q=compras")
    conteudo = response.content.decode()
    assert "Lista de compras" in conteudo
    assert "Reunião de equipe" not in conteudo


def test_remover_nota_via_post(client):
    client.post("/nova/", {"titulo": "Apagar depois", "conteudo": "conteúdo qualquer"})
    response = client.get("/")
    assert "Apagar depois" in response.content.decode()

    client.post("/1/remover/")
    response = client.get("/")
    assert "Apagar depois" not in response.content.decode()


def test_healthz_retorna_ok(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
