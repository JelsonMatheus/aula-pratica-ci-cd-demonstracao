import os


def versao_app(request):
    """Disponibiliza `versao_app` em todos os templates.

    Em produção (Cloud Run) o valor vem da variável de ambiente GIT_SHA,
    setada no momento do build da imagem Docker (veja Dockerfile e o
    workflow de deploy). É uma forma simples de provar, durante a aula,
    que um novo deploy realmente aconteceu: o rodapé da página muda.
    """
    sha = os.environ.get("GIT_SHA", "dev")
    return {"versao_app": sha[:7]}
