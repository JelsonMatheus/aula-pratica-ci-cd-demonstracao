## 1. Provedor OIDC: condição de atributo agora é obrigatória

Ao criar o provedor (`github-provider`) dentro do pool `github-pool` pela tela
**IAM e admin > Federação de identidade da carga de trabalho**, o Console exigiu um
campo que o comando `gcloud iam workload-identity-pools providers create-oidc` do
README não obriga: a **condição de atributo**.

Sem preencher esse campo, a criação falha com o erro:

```
The attribute condition must reference one of the provider's claims.
```

**Solução:** na seção "Condição de atributo" do formulário do provedor, adicionar uma
expressão CEL referenciando um claim do token do GitHub, por exemplo:

```
assertion.repository == "SEU_USUARIO/SEU_REPO"
```

Isso reforça (de forma redundante, mas agora obrigatória) a mesma restrição que o
binding de IAM do passo 2 também aplica.

Os demais campos do formulário:
- **Selecione um provedor**: OpenID Connect (OIDC)
- **Nome do provedor**: `github-provider`
- **Emissor (URL)**: `https://token.actions.githubusercontent.com`
- **Arquivo JWK (JSON)**: deixar em branco (o emissor é público)
- **Mapeamento de atributos**: `google.subject = assertion.sub` e
  `attribute.repository = assertion.repository`

## 2. Conta de serviço: onde fica o botão "Conceder acesso"

O binding que dá ao GitHub Actions permissão para "vestir" a conta `github-deployer`
(equivalente ao `add-iam-policy-binding` com `roles/iam.workloadIdentityUser`) não é
feito na tela de criação da conta, e o botão correspondente não fica visível de
primeira.

**Caminho:** IAM e admin > Contas de serviço > clicar no **e-mail** da conta
`github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com` (não no nome, no link do
e-mail) > aba **Permissões** > rolar a página para baixo até a seção
**"Principais com acesso a esta conta de serviço"** > o botão **Conceder acesso** está
dentro dessa seção específica, não no topo da página.

No formulário: colar em "Novos principais"
```
principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/SEU_USUARIO/SEU_REPO
```
e selecionar o papel **Workload Identity User**.

## 4. Permissão de escrita no Artifact Registry

Erro ao tentar publicar a imagem:
```
denied: Permission 'artifactregistry.repositories.uploadArtifacts' denied on resource
```

A conta `github-deployer` tinha permissão para *ser usada* (passo 2), mas não tinha
nenhum papel concedido *dentro do projeto*. São duas coisas diferentes.

**Caminho:** IAM e admin > **IAM** (página geral do projeto, diferente da página da
conta de serviço) > **Conceder acesso** > colar o e-mail
`github-deployer@SEU_PROJECT_ID.iam.gserviceaccount.com` > adicionar os papéis:
- **Artifact Registry Writer** (`roles/artifactregistry.writer`)
- **Cloud Run Admin** (`roles/run.admin`) — adicionado no mesmo passo, antecipando o
  erro do item 6.

Também foi necessário confirmar que o repositório Docker `bloco-notas` existe em
**Artifact Registry**, região `us-central1`, formato Docker/modo Standard (criar pela
tela se não existir).

## 5. API do Cloud Run não habilitada

Erro no step de deploy:
```
PERMISSION_DENIED: Cloud Run Admin API has not been used in project... before or it
is disabled.
```

O passo de habilitar APIs do README (`gcloud services enable ...`) não tinha sido
executado. **Solução:** clicar no link que o próprio erro fornece (abre a página da
API no Console com um botão **Ativar**), ou habilitar pela tela **APIs e serviços**.
Esperar 2–3 minutos de propagação antes de tentar de novo.

## 6. Permissão `iam.serviceaccounts.actAs` na conta padrão do Compute Engine

Erro:
```
Permission 'iam.serviceaccounts.actAs' denied on service account
PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

Como o workflow não especifica uma conta de serviço de execução para o Cloud Run, ele
tenta usar a conta padrão do Compute Engine — e quem faz o deploy precisa de permissão
para "agir como" essa conta.

**Solução (mais simples):** IAM e admin > IAM > editar o principal
`github-deployer@...` > adicionar o papel **Usuário da conta de serviço**
(`roles/iam.serviceAccountUser`).

**Alternativa mais restrita** (permissão só sobre essa conta específica, não sobre
todas as contas do projeto): IAM e admin > Contas de serviço > clicar no e-mail
`PROJECT_NUMBER-compute@developer.gserviceaccount.com` > aba Permissões > Conceder
acesso > colar o e-mail do `github-deployer` > papel **Usuário da conta de serviço**.

## 7. Serviço no ar, mas retornando 403 Forbidden

Depois de todos os passos anteriores, o deploy finalmente teve sucesso — mas a URL
pública respondia:
```
Error: Forbidden
Your client does not have permission to get URL / from this server.
```

Isso não é erro de configuração: por padrão, um serviço novo no Cloud Run nasce
**privado**, exigindo autenticação para qualquer requisição.

**Solução aplicada:** Cloud Run > serviço `bloco-notas` > aba Permissões > **Adicionar
principal** > principal `allUsers` > papel **Cloud Run Invoker** (`roles/run.invoker`).

Esse ajuste só precisa ser feito uma vez; deploys futuros pelo pipeline preservam essa
configuração (a própria Google recomenda não alternar isso via CI/CD, e sim deixá-lo
fixado direto no serviço).

## Resumo: papéis de IAM que `github-deployer` precisou acumular

| Papel | Onde foi concedido | Por quê |
|---|---|---|
| `roles/iam.workloadIdentityUser` | Na própria conta `github-deployer` (binding ao principalSet do WIF) | Permite que o GitHub Actions "vista" essa identidade |
| `roles/artifactregistry.writer` | IAM do projeto | Permite publicar a imagem Docker |
| `roles/run.admin` | IAM do projeto | Permite criar/atualizar o serviço no Cloud Run |
| `roles/iam.serviceAccountUser` | IAM do projeto (ou só na conta default do Compute Engine) | Permite "agir como" a conta que o Cloud Run usa para rodar o container |

E, fora da conta `github-deployer`: o principal `allUsers` precisou do papel
`roles/run.invoker` diretamente no serviço `bloco-notas`, para o site ficar acessível
publicamente.