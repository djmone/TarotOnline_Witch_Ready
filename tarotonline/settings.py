
import environ, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR/'.env')

SECRET_KEY = env('SECRET_KEY', default='dev-secret')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost:8080','http://127.0.0.1:8080'])

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'tarot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tarotonline.urls'

TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR/'templates'],
    'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'core.context.global_settings_context',
    ]}
}]

WSGI_APPLICATION = 'tarotonline.wsgi.application'
ASGI_APPLICATION = 'tarotonline.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


LANGUAGE_CODE = env('LANGUAGE_CODE', default='ru')
LANGUAGES = [('ru','Русский'),('en','English')]
TIME_ZONE = env('TIME_ZONE', default='Europe/Moscow')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

# Channels / WebSockets — локальный режим (без Redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LLM defaults
OLLAMA_BASE_URL = env('OLLAMA_BASE_URL', default='http://localhost:11434')
LLM_MODEL = env('LLM_MODEL', default='qwen2.5:14b')
LLM_TEMPERATURE = env.float('LLM_TEMPERATURE', 0.6)
LLM_MAX_TOKENS = env.int('LLM_MAX_TOKENS', 1200)

FREE_USES_DEFAULT = env.int('FREE_USES_DEFAULT', 2)
REVERSED_PROB = env.float('REVERSED_PROB', 0.5)
