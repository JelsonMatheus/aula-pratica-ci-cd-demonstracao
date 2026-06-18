# Bloco de Notas — projeto de demonstração de CI/CD

Projeto Django minimalista, criado para a aula prática de CI/CD com GitHub
Actions e GCP Cloud Run. **Propositalmente não usa banco de dados**: as
notas ficam guardadas na sessão do navegador (cookie assinado), então o
deploy não precisa de migrações nem de provisionar nenhum serviço de
banco de dados — o container fica 100% stateless.

## Funcionalidades

- Criar, editar, remover e buscar notas (título + conteúdo).
- Validações de negócio isoladas em `notas/services.py` (funções puras,
  sem Django/HTTP/sessão) — é aí que ficam a maior parte dos testes.
- Endpoint `/healthz/` para checagem de saúde no Cloud Run.
- Rodapé mostra o SHA do commit em produção, para comprovar visualmente
  que um novo deploy aconteceu durante a demonstração em aula.

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

export DJANGO_SECRET_KEY="qualquer-coisa-para-desenvolvimento"
export DJANGO_DEBUG=True

python manage.py runserver
```

Acesse http://127.0.0.1:8000/

## Verificando o estilo do código (Ruff)

```bash
ruff check .       # linter: verifica estilo e qualidade
ruff format --check .  # formatter: verifica a formatação sem alterar arquivos
```

Para corrigir os problemas automaticamente:

```bash
ruff check --fix .
ruff format .
```

O [Ruff](https://docs.astral.sh/ruff/) é o linter e formatter usado no projeto.
Ambas as verificações rodam antes dos testes na etapa de CI e bloqueiam o deploy
caso encontrem problemas no código.

## Rodando os testes

```bash
pytest -v
```

Os testes estão organizados em dois arquivos:

- `notas/tests/test_services.py` — testes unitários da lógica de negócio
  (a grande maioria, e os mais rápidos — não tocam em HTTP nem em sessão).
- `notas/tests/test_views.py` — testes de integração das rotas HTTP,
  usando o cliente de testes do Django.

## Build da imagem Docker

```bash
docker build --build-arg GIT_SHA=$(git rev-parse --short HEAD) -t bloco-notas .
docker run -p 8080:8080 -e DJANGO_SECRET_KEY=teste -e PORT=8080 bloco-notas
```

## Configurando o deploy automático (GCP + GitHub Actions)

1. Habilite as APIs necessárias no projeto GCP:

   ```bash
   gcloud services enable \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     iam.googleapis.com \
     sts.googleapis.com \
     iamcredentials.googleapis.com \
     --project=SEU_PROJECT_ID
   ```

2. Crie o repositório no Artifact Registry:

   ```bash
   gcloud artifacts repositories create bloco-notas \
     --repository-format=docker \
     --location=us-central1 \
     --project=SEU_PROJECT_ID
   ```

3. Configure a Workload Identity Federation (substitua os valores em
   maiúsculas):

   ```bash
   gcloud iam workload-identity-pools create "github-pool" \
     --project="SEU_PROJECT_ID" --location="global" \
     --display-name="GitHub Actions Pool"

   gcloud iam workload-identity-pools providers create-oidc "github-provider" \
     --project="SEU_PROJECT_ID" --location="global" \
     --workload-identity-pool="github-pool" \
     --display-name="GitHub provider" \
     --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
     --issuer-uri="https://token.actions.githubusercontent.com"

   gcloud iam service-accounts create "github-deployer" \
     --project="SEU_PROJECT_ID" \
     --display-name="GitHub Actions Deployer"

   gcloud iam service-accounts add-iam-policy-binding \
     "github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/iam.workloadIdentityUser" \
     --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/SEU_USUARIO/SEU_REPO"

   gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
     --member="serviceAccount:github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"

   gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
     --member="serviceAccount:github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/artifactregistry.writer"
   ```

4. No GitHub, vá em **Settings > Secrets and variables > Actions** do
   repositório e crie os secrets:

   | Secret | Valor |
   |---|---|
   | `GCP_PROJECT_ID` | ID do projeto GCP |
   | `GCP_WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
   | `GCP_SERVICE_ACCOUNT` | `github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com` |
   | `DJANGO_SECRET_KEY` | uma chave secreta aleatória para produção |

5. Faça um push para a branch `main`. O workflow em
   `.github/workflows/ci-cd.yml` vai: rodar os testes → (se passarem)
   buildar a imagem → enviar para o Artifact Registry → fazer o deploy
   no Cloud Run.

## Estrutura do projeto

```
demo_cicd/          # configuração do projeto Django (settings, urls)
notas/
  services.py        # lógica de negócio pura (o que mais é testado)
  views.py           # views HTTP, usam a sessão para guardar as notas
  context_processors.py
  templates/notas/
  tests/
    test_services.py
    test_views.py
Dockerfile
requirements.txt      # dependências de produção
requirements-dev.txt   # + pytest/pytest-django/ruff, usadas só na CI
.github/workflows/ci-cd.yml

```