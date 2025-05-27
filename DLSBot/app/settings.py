import os
from pathlib import Path
import environ
from datetime import timedelta


env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Настройки безопасности (сделал для тестирования вебапп)
SECURE_SSL_REDIRECT = (
    False  # Пока False, чтобы не было проблем, если что-то пойдет не так с HTTPS
)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Application definition

# TODO: Добавить Whitenoise для прод-версии
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_ckeditor_5",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_extensions",
    "app.core.apps.CoreConfig",
    "app.bot.apps.BotConfig",
    "app.learning_app.apps.LearningAppConfig",
    "app.organization.apps.OrganizationConfig",
    "app.integration.apps.IntegrationConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

# TODO: Добавить PostgreSQL для прод-версии + .env
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}



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

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# LOGIN_REDIRECT_URL = "/"

X_FRAME_OPTIONS = "SAMEORIGIN"

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
    "order_with_respect_to": [
        'bot',
        'learning_app',
        'organization',
        'integration',

        # Телеграм бот
        "bot.telegramuser",
        "bot.telegramgroup",
        "bot.usertest",
        "bot.userread",
        
        # Обучающие модули
        "learning_app.trainingcourse",
        "learning_app.coursetopic",
        "learning_app.topicquestion",
        "learning_app.answeroption",
        "learning_app.coursedirection",
        "learning_app.coursedeadline",
        "learning_app.tagcourse",
        "learning_app.certificate",
        "learning_app.ratingtrainingcourse",
        "learning_app.scormpack", #TODO: НЕ ВЫОДИТСЯ В МЕНЮ
        "learning_app.newsblock",

        # Справочники
        "organization.company",
        "organization.department",
        "organization.jobtitle",
        "organization.settingsbot",

        #Админ
        "auth.group",
        "auth.user",

        #Интеграция
        "integration.registrationsetting",
 
    ],
    # "icons": {
    #     "auth": "fas fa-users-cog",
    #     "auth.user": "fas fa-user",
    #     "auth.Group": "fas fa-users",
    #     "users.CustomUser": "fas fa-user",
    #     "educational_module.trainingcourse": "fas fa-book",
    #     "educational_module.coursetopic": "fas fa-list",
    #     "educational_module.coursedeadline": "fas fa-clock",
    #     "educational_module.scormpack": "fas fa-box",
    #     "educational_module.newsblock": "fas fa-newspaper",
    #     "educational_module.tagcourse": "fas fa-tags",
    #     "educational_module.certificate": "fas fa-certificate",
    #     "educational_module.ratingtrainingcourse": "fas fa-star",
    #     "educational_module.coursedirection": "fas fa-compass",
    #     "educational_module.topicquestion": "fas fa-question",
    #     "bot.telegramuser": "fas fa-user-graduate",
    #     "bot.telegramgroup": "fas fa-users",
    #     "educational_module.company": "fas fa-building",
    #     "reference_data.department": "fas fa-sitemap",
    #     "reference_data.jobtitle": "fas fa-id-badge",
    #     "educational_module.registrationsetting": "fas fa-cogs",
    #     "core.changelog": "fas fa-history",
    #     "admin.logentry": "fas fa-clipboard-list",
    #     "bot.useraction": "fas fa-user-clock",
    # },
}


    # "hide_apps": ['core', 'django_apscheduler', 'auth',],
    # "hide_models": ['admin.logentry', 'bot.useraction', 'bot.setslist', "bot.usertest",],
    # "order_with_respect_to": [
    #     'bot',
    #     'educational_module',
    #     'reference_data',
    #     # Телеграм бот
    #     "bot.telegramuser",
    #     "bot.telegramgroup",
    #     # Обучающие модули
    #     "educational_module.trainingcourse",
    #     "educational_module.coursetopic",
    #     "educational_module.topicquestion",
    #     "educational_module.coursedirection",
    #     "educational_module.coursedeadline",
    #     "educational_module.certificate",
    #     "educational_module.ratingtrainingcourse",
    #     "educational_module.scormpack",
    #     "educational_module.newsblock",
    #     "educational_module.tagcourse",
    #     "educational_module.company",
    #     "educational_module.registrationsetting",
    #     # Справочники
    #     "reference_data.department",
    #     "reference_data.jobtitle",
    #     # Пользователи
    #     "users.customuser",
    #     #Пока убрал!
    #     # "bot.useraction",
    #     # "bot.setslist",
    #     # "auth.group",
    #     # # Системные
    #     # "admin.logentry",
    #     # "django_apscheduler.djangojob",
    #     # "django_apscheduler.djangojobexecution",
    #     # "sites.site",
    #     # # Основной функционал
    #     # "core.changelog",
    #     # "core.requestlog",
    #     # "core.dynamicmodel",
    #     # "core.exchangelog",
    # ],
    # "icons": {
    #     "auth": "fas fa-users-cog",
    #     "auth.user": "fas fa-user",
    #     "auth.Group": "fas fa-users",
    #     "users.CustomUser": "fas fa-user",
    #     "educational_module.trainingcourse": "fas fa-book",
    #     "educational_module.coursetopic": "fas fa-list",
    #     "educational_module.coursedeadline": "fas fa-clock",
    #     "educational_module.scormpack": "fas fa-box",
    #     "educational_module.newsblock": "fas fa-newspaper",
    #     "educational_module.tagcourse": "fas fa-tags",
    #     "educational_module.certificate": "fas fa-certificate",
    #     "educational_module.ratingtrainingcourse": "fas fa-star",
    #     "educational_module.coursedirection": "fas fa-compass",
    #     "educational_module.topicquestion": "fas fa-question",
    #     "bot.telegramuser": "fas fa-user-graduate",
    #     "bot.telegramgroup": "fas fa-users",
    #     "educational_module.company": "fas fa-building",
    #     "reference_data.department": "fas fa-sitemap",
    #     "reference_data.jobtitle": "fas fa-id-badge",
    #     "educational_module.registrationsetting": "fas fa-cogs",
    #     "core.changelog": "fas fa-history",
    #     "admin.logentry": "fas fa-clipboard-list",
    #     "bot.useraction": "fas fa-user-clock",
    # },



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
        "success": "btn-success",
    },
}


CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
        ],
    }
}

# На будущее!

# CKEDITOR_5_CONFIGS = {
#     'default': {
#         'toolbar': ['heading', '|', 'bold', 'italic', 'link',
#                     'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

#     },
#     'extends': {
#         'blockToolbar': [
#             'paragraph', 'heading1', 'heading2', 'heading3',
#             '|',
#             'bulletedList', 'numberedList',
#             '|',
#             'blockQuote',
#         ],
#         'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
#         'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
#                     'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'imageUpload', '|',
#                     'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
#                     'insertTable',],
#         'image': {
#             'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
#                         'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
#             'styles': [
#                 'full',
#                 'side',
#                 'alignLeft',
#                 'alignRight',
#             ]
#         },
#         'table': {
#             'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
#             'tableProperties', 'tableCellProperties' ],
#             'tableProperties': {
#                 'borderColors': 'custom',
#                 'backgroundColors': 'custom'
#             },
#             'tableCellProperties': {
#                 'borderColors': 'custom',
#                 'backgroundColors': 'custom'
#             }
#         },
#         'heading' : {
#             'options': [
#                 { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
#                 { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
#                 { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
#                 { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
#             ]
#         }
#     },
#     'list': {
#         'properties': {
#             'styles': 'true',
#             'startIndex': 'true',
#             'reversed': 'true',
#         }
#     }
# }

# Пути для загрузки файлов через CKEditor 5 (относительно MEDIA_ROOT)
CKEDITOR_5_UPLOAD_PATH = "uploads/"
CKEDITOR_5_IMAGE_UPLOAD_PATH = "images/"  # отдельный путь для картинок
CKEDITOR_5_CSRF_COOKIE_NAME = "csrftoken"

# Пути к сертификатам
SSL_CERTIFICATE_PATH = BASE_DIR / "cert.pem"
SSL_KEY_PATH = BASE_DIR / "key.pem"

# Команда для запуска сервера с SSL по умолчанию
RUNSERVERPLUS_SERVER_ADDRESS_PORT = "0.0.0.0:8000"
RUNSERVERPLUS_EXTRA_OPTIONS = (
    f"--cert-file {SSL_CERTIFICATE_PATH} --key-file {SSL_KEY_PATH}"
)

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
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
