"""
Django settings for conf project.
"""
from django_env import Env
from pathlib import Path

SETTINGS_DIR = Path(__file__).resolve().parent
DJANGO_BASE = SETTINGS_DIR.parent
PROJECT_BASE = DJANGO_BASE.parent

env = Env()
if env.bool('DJANGO_READ_DOTENV_FILE', True):
    env.read_env(search_path=PROJECT_BASE, parents=True)

SECRET_KEY = env.get('DJANGO_SECRET_KEY')
DEBUG = env.get('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.get('DJANGO_ALLOWED_HOSTS', default=[])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRDPARTY_APPS = []
CUSTOM_APPS = [
    'core'
]
INSTALLED_APPS = DJANGO_APPS + CUSTOM_APPS + THIRDPARTY_APPS

DJANGO_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
THIRDPARTY_MIDDLEWARE = []
CUSTOM_MIDDLEWARE = []
MIDDLEWARE = DJANGO_MIDDLEWARE + CUSTOM_MIDDLEWARE + THIRDPARTY_MIDDLEWARE

ROOT_URLCONF = 'core.urls'

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

if env.bool('DJANGO_TEMPLATE_CACHE', False):
    TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS)
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            DJANGO_BASE / 'templates'
        ],
        'OPTIONS': {
            'loaders': TEMPLATE_LOADERS,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

DATABASE_MAP = {
    'default': ('DJANGO_DATABASE_URL',),
    'readonly': ('DJANGO_DATABASE_RO_URL'),
    'postgres': ('DJANGO_POSTGRES_URL',),
}

DATABASES = {name: env.database_url(var) for name, var in DATABASE_MAP.items() if env.is_set(var)}

CACHES = {
    'default': env.cache_url('DJANGO_CACHE_URL')
}

vars().update(env.email_url('DJANGO_EMAIL_URL', default="consolemail://"))

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = env.get('DJANGO_LANG', 'en-AU')
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
