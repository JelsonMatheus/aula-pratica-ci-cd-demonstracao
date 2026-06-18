"""
Configurações do projeto demo_cicd (Bloco de Notas).

Projeto pensado para a aula de CI/CD: propositalmente NÃO usa banco de
dados. As notas ficam guardadas na sessão do usuário, armazenada em um
cookie assinado (signed_cookies). Isso significa:

  - Nenhuma migração para rodar no deploy.
  - Nenhum serviço de banco de dados (Cloud SQL etc.) para provisionar.
  - O container é totalmente stateless -> ótimo para Cloud Run.

Para um projeto real você normalmente usaria um banco de dados de verdade
(Postgres no Cloud SQL, por exemplo). Aqui o objetivo é manter o foco da
aula no pipeline de CI/CD, não na modelagem de dados.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(nome, padrao=False):
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in ("1", "true", "yes", "on")


# SECURITY WARNING: defina DJANGO_SECRET_KEY em produção!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-apenas-para-desenvolvimento-local-nao-usar-em-producao",
)

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

# Cloud Run usa o cabeçalho X-Forwarded-Proto para indicar HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# --- Apenas o essencial: sem admin, auth ou contenttypes (não há DB) ---
INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "notas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "demo_cicd.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "notas.context_processors.versao_app",
            ],
        },
    },
]

WSGI_APPLICATION = "demo_cicd.wsgi.application"

# --- Sem banco de dados: notas vivem na sessão (cookie assinado) ---
DATABASES = {}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 dias

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
