import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import environ

env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(env.str("ENV_PATH", ".env"))

BASE_DIR = Path(__file__).resolve().parent.parent

# Пути к сертификатам
SSL_CERTIFICATE_PATH = BASE_DIR / "cert.pem"
SSL_KEY_PATH = BASE_DIR / "key.pem"

# Команда для запуска сервера с SSL по умолчанию
RUNSERVERPLUS_SERVER_ADDRESS_PORT = "0.0.0.0:8000"
RUNSERVERPLUS_EXTRA_OPTIONS = (
    f"--cert-file {SSL_CERTIFICATE_PATH} --key-file {SSL_KEY_PATH}"
)


SECRET_KEY = env("SECRET_KEY", default="0")

DEBUG = env("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

INSTALLED_APPS = [
    # 'jet.dashboard',
    # 'jet',
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app.bot",
    "app.core",
    "app.educational_module",
    "app.reference_data",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "django_filters",
    "users",
    "ckeditor",
    "ckeditor_uploader",
    "django_extensions",
    "sslserver",
    "colorfield",
    "django_apscheduler",
    "solo",
]

# AUTHENTICATION_BACKENDS = ['app.authentication.EmailBackend']

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.core.middleware.LoggedInUserMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

BOT_TOKEN = env("BOT_TOKEN")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
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

WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        #     'ENGINE': 'django.db.backends.postgresql',
        #     'NAME': env('DB_NAME', default='None'),
        #     'USER': env('DB_USER', default='None'),
        #     'PASSWORD': env('DB_PWD', default='None'),
        #     'HOST': env('DB_HOST', default='None'),
        #     'PORT': env('DB_PORT', default='None'),
        # },
        # 'sqlite': {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "ru"
LANGUAGES = (
    ("ru", _("Russia")),
    # ('en', _('English')),
    # ('uz', _("O'zbek tili")),
)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / "locale"]
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")


JAZZMIN_SETTINGS = {
    "site_title": "СДО",
    "site_header": "СДО",
    "site_brand": "СДО",
    "site_logo": "logo/logo.png",
    "site_logo_classes": "img-square",
    "copyright": "CDTEK",
    "welcome_sign": "Добро пожаловать в СДО",
    "related_modal_active": True,
    "show_ui_builder": True,

    "hide_apps": ['core', 'django_apscheduler', 'auth',],
    "hide_models": ['admin.logentry', 'bot.useraction', 'bot.setslist', "bot.usertest",],
    "order_with_respect_to": [
        'bot',
        'educational_module',
        'reference_data',

        # Телеграм бот
        "bot.telegramuser",
        "bot.telegramgroup",

        # Обучающие модули
        "educational_module.trainingcourse",
        "educational_module.coursetopic",
        "educational_module.topicquestion",
        "educational_module.coursedirection",
        "educational_module.coursedeadline",
        "educational_module.certificate",
        "educational_module.ratingtrainingcourse",
        "educational_module.scormpack",
        "educational_module.newsblock",
        "educational_module.tagcourse",
        "educational_module.company",
        "educational_module.registrationsetting",

        # Справочники
        "reference_data.department",
        "reference_data.jobtitle",

        # Пользователи
        "users.customuser",
        
        #Пока убрал!
        # "bot.useraction",
        # "bot.setslist",
        # "auth.group",
        # # Системные
        # "admin.logentry",
        # "django_apscheduler.djangojob",
        # "django_apscheduler.djangojobexecution",
        # "sites.site",
        # # Основной функционал
        # "core.changelog",
        # "core.requestlog",
        # "core.dynamicmodel",
        # "core.exchangelog",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.CustomUser": "fas fa-user",
        "educational_module.trainingcourse": "fas fa-book",
        "educational_module.coursetopic": "fas fa-list",
        "educational_module.coursedeadline": "fas fa-clock",
        "educational_module.scormpack": "fas fa-box",
        "educational_module.newsblock": "fas fa-newspaper",
        "educational_module.tagcourse": "fas fa-tags",
        "educational_module.certificate": "fas fa-certificate",
        "educational_module.ratingtrainingcourse": "fas fa-star",
        "educational_module.coursedirection": "fas fa-compass",
        "educational_module.topicquestion": "fas fa-question",
        "bot.telegramuser": "fas fa-user-graduate",
        "bot.telegramgroup": "fas fa-users",
        "educational_module.company": "fas fa-building",
        "reference_data.department": "fas fa-sitemap",
        "reference_data.jobtitle": "fas fa-id-badge",
        "educational_module.registrationsetting": "fas fa-cogs",
        "core.changelog": "fas fa-history",
        "admin.logentry": "fas fa-clipboard-list",
        "bot.useraction": "fas fa-user-clock",
    },    
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "united",
    "dark_mode_theme": "slate",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

LOGIN_REDIRECT_URL = "/"

X_FRAME_OPTIONS = "SAMEORIGIN"

REST_FRAMEWORK = {
    # 'DATETIME_FORMAT': '%s000',
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "app.renderers.UTF8CharsetJSONRenderer",
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

INTERNAl_IPS = ["localhost", "127.0.0.1"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# Setup support for proxy headers
if not DEBUG:
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Кастомная модель User
AUTH_USER_MODEL = "users.CustomUser"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "width": "100%",
        "height": "400px",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "apscheduler": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "app.lightning": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
