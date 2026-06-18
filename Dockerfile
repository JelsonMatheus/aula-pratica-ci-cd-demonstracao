# Imagem de produção do Bloco de Notas, pensada para rodar no Cloud Run.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala apenas as dependências de produção (sem pytest etc.)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SHA do commit, injetado pelo workflow de deploy (docker build --build-arg GIT_SHA=...)
# Usado só para mostrar a versão em produção no rodapé da página.
ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA}

EXPOSE 8080

# O Cloud Run injeta a variável $PORT (padrão 8080) e espera que o
# processo escute nela. Sem migrações para rodar: o app não usa banco.
CMD exec gunicorn demo_cicd.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 4 \
    --timeout 0
