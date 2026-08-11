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

# TODO - добавить дополнительные настройки CORS для более полной конфигурации
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CORS_EXPOSE_HEADERS = [
    "Content-Disposition",
    "X-Scorm-Name-Index",
]

# Настройки безопасности (сделал для тестирования вебапп
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
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
    "drf_spectacular",
    "django_extensions",
    "import_export",
    "app.core.apps.CoreConfig",
    "app.bot.apps.BotConfig",
    "app.learning_app.apps.LearningAppConfig",
    "app.organization.apps.OrganizationConfig",
    "app.integration.apps.IntegrationConfig",
    "app.scheduler.apps.SchedulerConfig",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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


ENVIRONMENT = env("ENVIRONMENT", default="dev")

if ENVIRONMENT == "prod":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PWD", default=""),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
        }
    }
else:
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
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",  # 100 запросов в час для анонимов
        "user": "1000/hour",  # 1000 запросов в час для авторизованных
        "login": "100/hour",  # 10 попыток входа в час
        "password_reset": "50/hour",  # 3 попытки сброса пароля в час
    },
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=520),
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
    "USER_ID_CLAIM": "user_id", #!!!123
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
    "site_brand": None,
    "site_icon": "logo/favicon.png",
    "site_logo": "logo/eng-logo.png",
    "login_logo": None,
    "site_logo_classes": "custom-logo-style",
    "copyright": 'Проект компании ООО "ЦЦ ТЭК" | cdtek.ru',
    "welcome_sign": "Добро пожаловать в СДО",
    "related_modal_active": True,
    "show_ui_builder": False,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/admin_row_dimming.js",
    "topmenu_links": [
        {"name": "Статистика", "url": "admin-statistics-education", "icon": "fas fa-chart-bar"},
    ],
    "hide_models": [
        "bot.passwordresettoken",
    ],
    "order_with_respect_to": [
        "bot",
        "learning_app",
        "organization",
        "integration",
        "scheduler",
        # Телеграм бот
        "bot.customuser",
        "bot.telegramuser",
        "bot.telegramgroup",
        "bot.userread",
        "bot.usertest",
        "bot.passwordresettoken",
        "bot.userratings",
        "bot.subscription",
        # Обучающие модули
        "learning_app.trainingcourse",
        "learning_app.coursetopic",
        "learning_app.topicquestion",
        "learning_app.answeroption",
        "learning_app.coursedirection",
        "learning_app.coursedeadline",
        "learning_app.obligatorylist",
        "learning_app.tagcourse",
        "learning_app.certificate",
        "learning_app.ratingtrainingcourse",
        "learning_app.scormpack",
        "learning_app.newsblock",
        "learning_app.usernewsstatus",
        "learning_app.courseassignmentnotification",
        # Планировщик
        "scheduler.remindersetting",
        "scheduler.schedulerlog",
        # Справочники
        "organization.company",
        "organization.department",
        "organization.jobtitle",
        "organization.settingsbot",
        # Админ
        "auth.user",
        "auth.group",
        # Интеграция
        "integration.registrationsetting",
        #"integration.apisettings",
    ],
    "icons": {
        # Admin
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "admin.logentry": "fas fa-clipboard-list",
        # Bot
        "bot": "fas fa-robot",
        "bot.telegramuser": "fas fa-user-graduate",
        "bot.telegramgroup": "fas fa-users",
        "bot.userread": "fas fa-book-reader",
        "bot.usertest": "fas fa-tasks",
        "bot.passwordresettoken": "fas fa-key",
        "bot.userratings": "fas fa-star",
        "bot.subscription": "fas fa-bell",
        # Learning App
        "learning_app": "fas fa-graduation-cap",
        "learning_app.trainingcourse": "fas fa-book",
        "learning_app.coursetopic": "fas fa-list-alt",
        "learning_app.topicquestion": "fas fa-question-circle",
        "learning_app.answeroption": "fas fa-check-square",
        "learning_app.coursedirection": "fas fa-compass",
        "learning_app.coursedeadline": "fas fa-clock",
        "learning_app.obligatorylist": "fas fa-list-check",
        "learning_app.tagcourse": "fas fa-tags",
        "learning_app.certificate": "fas fa-certificate",
        "learning_app.ratingtrainingcourse": "fas fa-star",
        "learning_app.scormpack": "fas fa-file-archive",
        "learning_app.newsblock": "fas fa-newspaper",
        "learning_app.usernewsstatus": "fas fa-eye",
        "learning_app.courseassignmentnotification": "fas fa-bell",
        # Scheduler
        "scheduler": "fas fa-clock",
        "scheduler.remindersetting": "fas fa-clock",
        "scheduler.schedulerlog": "fas fa-list-alt",
        # Organization
        "organization": "fas fa-sitemap",
        "organization.company": "fas fa-building",
        "organization.department": "fas fa-building",
        "organization.jobtitle": "fas fa-id-badge",
        "organization.settingsbot": "fas fa-cog",
        # Integration
        "integration": "fas fa-plug",
        "integration.registrationsetting": "fas fa-cogs",
        #"integration.apisettings": "fas fa-cogs",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-secondary",  # акцент подчёркивания/чекбоксов
    "navbar": "navbar-white navbar-light",  # поменял на белый
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": True,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-primary",  # поменял на белый можно light-info/light-secondary и т.д.
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    # "button_classes": {
    #     "primary": "btn-outline-primary",
    #     "secondary": "btn-outline-secondary",
    #     "info": "btn-info",
    #     "warning": "btn-warning",
    #     "danger": "btn-danger",
    #     "success": "btn-success",
    # },
    "button_classes": {
        "primary": "btn-dark",
        "secondary": "btn-dark",
        "info": "btn-dark",
        "warning": "btn-dark",
        "danger": "btn-dark",
        "success": "btn-dark",
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
            "blockQuote",
            "imageUpload",
        ],
    },
    "extends": {
        "blockToolbar": [
            "paragraph",
            "heading1",
            "heading2",
            "heading3",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "blockQuote",
        ],
        "toolbar": [
            "heading",
            "|",
            "outdent",
            "indent",
            "|",
            "bold",
            "italic",
            "link",
            "underline",
            "strikethrough",
            "code",
            "subscript",
            "superscript",
            "highlight",
            "|",
            "codeBlock",
            "sourceEditing",
            "insertImage",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "imageUpload",
            "|",
            "fontSize",
            "fontFamily",
            "fontColor",
            "fontBackgroundColor",
            "mediaEmbed",
            "removeFormat",
            "insertTable",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "|",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
                "imageStyle:side",
                "|",
            ],
            "styles": [
                "full",
                "side",
                "alignLeft",
                "alignRight",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
            "tableProperties": {"borderColors": "custom", "backgroundColors": "custom"},
            "tableCellProperties": {
                "borderColors": "custom",
                "backgroundColors": "custom",
            },
        },
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading1",
                    "view": "h1",
                    "title": "Heading 1",
                    "class": "ck-heading_heading1",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
    },
    "list": {
        "properties": {
            "styles": "true",
            "startIndex": "true",
            "reversed": "true",
        }
    },
}

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


AUTH_USER_MODEL = "bot.CustomUser"

# # =========================
# # EMAIL SETTINGS
# # =========================
# # TODO: Настроить реальный SMTP провайдер (Яндекс.Почта, Mail.ru и т.д.)
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # Для разработки
# # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Для продакшена
# # EMAIL_HOST = 'smtp.yandex.ru'
# # EMAIL_PORT = 587
# # EMAIL_USE_TLS = True
# # EMAIL_HOST_USER = 'your-email@yandex.ru'
# # EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = "noreply@sdo.local"


# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'stepanychev2101@gmail.com'
# EMAIL_HOST_PASSWORD = ''
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# =========================
# EMAIL SETTINGS
# =========================
# Включаем реальную отправку по SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Данные SMTP-сервера
EMAIL_HOST = 'm.gatewaymail.net'
EMAIL_USE_TLS    = False
EMAIL_USE_SSL    = False
EMAIL_PORT       = 587
# Учетные данные
EMAIL_HOST_USER = 'dls@engsdrilling.ru'
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
# Адрес, от которого будут приходить письма
DEFAULT_FROM_EMAIL = 'dls@engsdrilling.ru'


# URL фронтенда для ссылок в письмах
FRONTEND_URL = "http://localhost:3000"

# =========================
# DRF SPECTACULAR SETTINGS
# =========================
SPECTACULAR_SETTINGS = {
    "TITLE": "СДО API Documentation",
    "DESCRIPTION": "API документация для системы дистанционного обучения",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Дополнительные настройки для JWT аутентификации
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    # Настройки безопасности для JWT
    "SECURITY": [
        {
            "type": "http",
            "name": "Authorization",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    ],
    # Схема аутентификации
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # Настройки UI
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelRendering": "model",
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    },
    # Настройки Redoc
    "REDOC_UI_SETTINGS": {
        "hideDownloadButton": False,
        "hideHostname": False,
        "hideLoading": False,
        "hideSchemaPattern": True,
        "expandResponses": "200,201",
        "pathInMiddlePanel": True,
        "nativeScrollbars": False,
        "theme": {
            "colors": {"primary": {"main": "#1976d2"}},
            "typography": {
                "fontSize": "14px",
                "lineHeight": "1.5em",
                "code": {"fontSize": "13px"},
            },
        },
    },
    # Настройки для сортировки эндпоинтов
    "SORT_OPERATION_PARAMETERS": True,
    "SORT_OPERATIONS": True,
    # Исключаем некоторые эндпоинты из документации если нужно
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": None,
}
