import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(env.str('ENV_PATH', '.env'))

BASE_DIR = Path(__file__).resolve().parent.parent

# Пути к сертификатам
SSL_CERTIFICATE_PATH = BASE_DIR / 'cert.pem'
SSL_KEY_PATH = BASE_DIR / 'key.pem'

# Команда для запуска сервера с SSL по умолчанию
RUNSERVERPLUS_SERVER_ADDRESS_PORT = '0.0.0.0:8000'
RUNSERVERPLUS_EXTRA_OPTIONS = f'--cert-file {SSL_CERTIFICATE_PATH} --key-file {SSL_KEY_PATH}'


SECRET_KEY = env('SECRET_KEY', default='0')

DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.bot',
    'app.core',
    'app.educational_module',
    'app.lightning',
    'rest_framework_swagger',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'users',
    'ckeditor',
    'ckeditor_uploader',
    'django_extensions',
    'sslserver',
    'colorfield',
]

# AUTHENTICATION_BACKENDS = ['app.authentication.EmailBackend']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.core.middleware.LoggedInUserMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

BOT_TOKEN = env("BOT_TOKEN")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
    'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': env('DB_NAME', default='None'),
    #     'USER': env('DB_USER', default='None'),
    #     'PASSWORD': env('DB_PWD', default='None'),
    #     'HOST': env('DB_HOST', default='None'),
    #     'PORT': env('DB_PORT', default='None'),
    # },
    # 'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('ru', _('Russia')),
    ('en', _('English')),
    ('uz', _("O'zbek tili")),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / 'locale'
]
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
# MEDIA_URL = 'http://127.0.0.1:8000/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JET_CHANGE_FORM_SIBLING_LINKS = True

JET_SIDE_MENU_COMPACT = True

JET_INDEX_DASHBOARD = 'app.dashboard.CustomDashboard'

JET_SIDE_MENU_ITEMS = [
    {'label': _('Обучение:'),
     'items': [
        {'name': 'educational_module.trainingcourse', 'label': _('Обучающие программы')},
        {'name': 'educational_module.coursedirection', 'label': _('Направления ПО')},          
        {'name': 'bot.telegramuser', 'label': _('Студенты')},
        {'name': 'bot.telegramgroup', 'label': _('Группы студентов')},
        #  {'name': 'bot.setslist', 'label': _('Settings_JET_MENU_ITEMS')},
        {'label': 'Статистика'}
         
     ]},
    {'label': _('Молния:'),
     'items': [
        {'name': 'lightning.lightning', 'label': _('Молнии')},
        {'name': 'lightning.jobtitle', 'label': _('Должности')},
        {'name': 'lightning.lightningmessage', 'label': _('Сообщения молнии')},
        {'name': 'lightning.lightningquestion', 'label': _('Вопросы молнии')},
        {'name': 'lightning.lightninganswer', 'label': _('Варианты ответов молнии')},
        {'name': 'bot.telegramuser', 'label': _('Пользователи')},
        {'name': 'bot.telegramgroup', 'label': _('Группы')},
        {'label': 'Статистика'}
         
     ]},    
    # {'label': _('Educational_JET_MENU_ITEMS'), 
    #  'items': [
        # {'name': 'educational_module.coursetopic', 'label': _('Разделы программы обучения')},
        # {'name': 'educational_module.topicquestion', 'label': _('TopicQuestion_JET_MENU_ITEMS')},
        # {"label": _('Educational_bot_JET_MENU_ITEMS'), "url": "https://t.me/Energy_Oil_and_Gas_Service_bot"}
    # ]},
    {'label': _('Администрирование'), 'permissions': ['user.user'], 
     'items': [
        # {'name': 'auth.user', 'label': _('Users_JET_MENU_ITEMS')},
        {'name': 'educational_module.company', 'label': _('Организации')},        
        {'name': 'users.customuser', 'label': _('Пользователи')},
        {'name': 'auth.group', 'label': _('Группы пользователей')},
        {'name': 'core.changelog', 'label': _('Логирование телеграм')},
        {'name': 'admin.logentry', 'label': _('Логирование админ-панели')},        
        {'name': 'bot.useraction', 'label': _('Логирование телеграм2')},
        # {'name': 'core.exchangelog', 'label': _('Exchange logging_JET_MENU_ITEMS')},
        # {'name': 'core.requestlog', 'label': _('Request logging_JET_MENU_ITEMS')},
    ]},
    # {'label': _('APIDocs_JET_MENU_ITEMS'), 'permissions': ['user.user'], 'items': [
    #     {'name': '-', 'label': _('Swagger_JET_MENU_ITEMS'), 'url': '/api-swagger/', 'url_blank': True},
    #     {'name': '-', 'label': _('redoc_JET_MENU_ITEMS'), 'url': '/api-redoc/', 'url_blank': True},
    # ]},
]

JET_DEFAULT_THEME = 'engs'

JET_THEMES = [
    # {
    #     'theme': 'default',
    #     'color': '#47bac1',
    #     'title': 'Default'
    # },
    # {
    #     'theme': 'green',
    #     'color': '#44b78b',
    #     'title': 'Green'
    # },
    # {
    #     'theme': 'light-green',
    #     'color': '#2faa60',
    #     'title': 'Light Green'
    # },
    # {
    #     'theme': 'light-gray',
    #     'color': '#222',
    #     'title': 'Light Gray'
    # },
    {
        'theme': 'engs',
        'color': '#00234b',
        'title': 'ENGS'
    }
]

LOGIN_REDIRECT_URL = "/"

X_FRAME_OPTIONS = 'SAMEORIGIN'

REST_FRAMEWORK = {
    # 'DATETIME_FORMAT': '%s000',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'app.renderers.UTF8CharsetJSONRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
}

INTERNAl_IPS = [
    'localhost',
    '127.0.0.1'
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Setup support for proxy headers
if not DEBUG:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Кастомная модель User
AUTH_USER_MODEL = 'users.CustomUser'

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': '100%',
        'height': '400px',
    },
}