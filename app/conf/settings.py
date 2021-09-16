# -*- coding: utf-8 -*-
"""
Django settings for conf project.
"""
from django.contrib import messages
from django_env import Env
from pathlib import Path

SETTINGS_DIR = Path(__file__).resolve().parent
DJANGO_ROOT = SETTINGS_DIR.parent
PROJECT_ROOT = DJANGO_ROOT.parent

env = Env()
if env.bool('DJANGO_READ_DOTENV_FILE', True):
    env.read_env(search_path=PROJECT_ROOT, parents=True)

SECRET_KEY = env.get('DJANGO_SECRET_KEY')
DEBUG = env.get('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.get('DJANGO_ALLOWED_HOSTS', default=[])

ADMIN_ENABLED = env.bool('DJANGO_ADMIN_ENABLED', default=True)

# required for flatpages
SITE_ID = env.int('SITE_ID', 1)

# Application definition

DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
]

if ADMIN_ENABLED:
    # we WANT an error if this setting is used by unguarded code
    ADMIN_URL = 'admin/'
    DJANGO_APPS.insert(0, 'django.contrib.admin')

THIRDPARTY_APPS = [
    'rest_framework',
    'sitetree',
    'markdownx',
    'taggit',
]
CUSTOM_APPS = [
    'core.cachedmodel',
    'core',
    #'modules.pages',
    #'modules.articles',
]
INSTALLED_APPS = DJANGO_APPS + CUSTOM_APPS + THIRDPARTY_APPS

DJANGO_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]
THIRDPARTY_MIDDLEWARE = [
]
CUSTOM_MIDDLEWARE = []
EXTRA_MIDDLEWARE = [
    'django.middleware.cache.FetchFromCacheMiddleware',  # must be last
]
MIDDLEWARE = DJANGO_MIDDLEWARE + CUSTOM_MIDDLEWARE + THIRDPARTY_MIDDLEWARE + EXTRA_MIDDLEWARE

ROOT_URLCONF = 'conf.urls'

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
            DJANGO_ROOT / 'templates',
        ],
        'OPTIONS': {
            'loaders': TEMPLATE_LOADERS,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.fontawesome',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'
ASGI_APPLICATION = 'conf.asgi:application'

DATABASE_MAP = {
    'default': ('DJANGO_DATABASE_URL', {}),
    'readonly': ('DJANGO_DATABASE_RO_URL', {'readonly': True}),
    'postgres': ('DJANGO_POSTGRES_URL', {}),
}
DATABASES = {
    name: env.database_url(var, options=opts)
    for name, (var, opts) in DATABASE_MAP.items() if env.is_set(var)
}
DATABASE_ROUTERS = ['core.components.db_router.DBRouter']

CACHES = {
    'default': env.cache_url('DJANGO_CACHE_URL'),
    'sessions': env.cache_url('DJANGO_SESSIONS_CACHE_URL', default=env.get('DJANGO_CACHE_URL'))
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


vars().update(env.email_url('DJANGO_EMAIL_URL', default="consolemail://"))

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]
# support authentication using username or email
AUTHENTICATION_BACKENDS = [
    'core.components.auth.EmailOrUsernameAuthBackend',
]

LANGUAGE_CODE = env.get('DJANGO_LANG', 'en-AU')
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# django-sass-compiler
SCSS_ROOT = DJANGO_ROOT / 'scss'
SCSS_COMPILE = ['**/*.scss']
CSS_COMPILE_DIR = SCSS_ROOT
CSS_STYLE = 'compressed'
SCSS_INCLUDE_PATHS = [
    PROJECT_ROOT / 'node_modules'
]

STATIC_URL = env.get('DJANGO_STATIC_URL', '/static/')
STATICFILES_DIRS = [  # where (non-app_ static files are discovered
    DJANGO_ROOT / 'static'
]
STATICFILES_FINDERS = [
    'npm.finders.NpmFinder',                                    # node_modules
    'django_sass_finder.finders.ScssFinder',                    # scss files
    'django.contrib.staticfiles.finders.FileSystemFinder',      # STATICFILES_DIRS
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  # {app}/static
]
STATIC_ROOT = str(PROJECT_ROOT / 'static')        # where static files are collected
NPM_ROOT_PATH = str(PROJECT_ROOT)
FONTAWESOME = 'fontawesome-pro'
CORE_ICON_FONTSET = FONTAWESOME
NPM_FILE_PATTERNS = {
    'mini.css': [
        'dist/*'
    ],
    '@fortawesome': [
        f'{FONTAWESOME}/css/*.css',
        f'{FONTAWESOME}/webfonts/*',
    ],
    'htmx.org': [
        'dist/*'
    ]
}

MEDIA_ROOT = str(PROJECT_ROOT / 'media')
MEDIA_URL = env.get('DJANGO_MEDIA_URL', '/media/')

## Third party config
# markdownx
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',        # built in combo
    'markdown.extensions.codehilite',   # syntax highlighting using pygments
    'markdown.extensions.meta',
    'markdown.extensions.toc',          # table of contents [TOC]
    'markdown_markup_emoji.markup_emoji',
    'mdx_emoticons',
]
MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
    'mdx_emoticons': {
        'base_url': f"{MEDIA_URL}emoticons/",
        'file_extension': 'gif'
    }
}
MARKDOWNX_URLS_PATH = '/markdownx/markdownify/'
MARKDOWNX_UPLOAD_URLS_PATH = '/markdownx/upload/'
MARKDOWNX_UPLOAD_MAX_SIZE = 50 * 1024 * 1024
MARKDOWNX_UPLOAD_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/svg+xml', 'image/webp']
MARKDOWNX_SERVER_CALL_LATENCY = 2500
# @TODO: this needs to be lazily evaluated each time
# MARKDOWNX_MEDIA_PATH = timezone.now().strftime('media/uploads/%Y_%m/')
