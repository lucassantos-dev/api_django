from pathlib import Path
from os import getenv, path
import dotenv
from django.core.management.utils import get_random_secret_key

# Define o caminho da pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'api.urls'
# Carrega as variáveis de ambiente a partir do arquivo .env.local
dotenv_file = BASE_DIR / ".env.local"
if path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# Configurações gerais do projeto
SECRET_KEY = getenv("DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0,192.168.1.54").split(",")
DOWNLOAD_FOLDER = "/home/dev/Documents/files"

# Definição dos aplicativos instalados no projeto
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "users",
    "djoser",
    'drf_yasg',
    "attendants",
    "protocols",
    "digisac",
]

# Configuração dos middlewares utilizados no projeto
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Configuração das templates utilizadas no projeto
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Configuração do arquivo WSGI utilizado para servir o projeto
WSGI_APPLICATION = "api.wsgi.application"

# Configuração do Swagger (drf_yasg) para documentação da API
SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
}

# Configuração do banco de dados (SQLite por padrão)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Configuração de validadores de senha
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Configurações de internacionalização
LANGUAGE_CODE = "pt-BR"
TIME_ZONE = 'America/Fortaleza'
USE_I18N = True
USE_TZ = True

# Configuração do modelo de autenticação
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Configuração de arquivos estáticos e media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Configurações do Django Rest Framework (DRF)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.CustomJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Configurações do Djoser para autenticação de usuários
DJOSER = {
    'SERIALIZERS': {
        'user': 'users.serializers.CustomUserSerializer',
    },
    "TOKEN_MODEL": None,
}

# Configurações de cookies de autenticação
AUTH_COOKIE = "access"
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24
AUTH_COOKIE_SECURE = getenv("AUTH_COOKIE_SECURE", "True") == "True"
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = "/"
AUTH_COOKIE_SAMESITE = "None"

# Configurações de CORS
CORS_ALLOWED_ORIGINS = getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# Configuração do modelo de ID padrão (auto field)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuração do modelo de usuário personalizado
AUTH_USER_MODEL = "users.UserAccount"

#Configuração da Api do DIGISAC
URL_API_DIGISAC= getenv("URL_API_DIGISAC")
TOKEN_API_DIGISAC= getenv("TOKEN_API_DIGISAC")