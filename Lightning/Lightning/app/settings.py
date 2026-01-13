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

# Настройки безопасности (сделал для тестирования вебапп)
SECURE_SSL_REDIRECT = (
    False  # Пока False, чтобы не было проблем, если что-то пойдет не так с HTTPS
)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

"""Настройки для большого количества полей в форме"""
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_ckeditor_5",
    "django_extensions",
    "import_export",
    "django_object_actions",
    "app.bot",
    "app.core",
    "app.lightning",
    "app.organization",
    "app.dozor",
    "app.scheduler",
    "app.integration",
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

DATABASES = {
    "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME", default="None"),
            "USER": env("DB_USER", default="None"),
            "PASSWORD": env("DB_PWD", default="None"),
            "HOST": env("DB_HOST", default="None"),
            "PORT": env("DB_PORT", default="None"),
        },
        "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
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


JAZZMIN_SETTINGS = {
    "site_title": "Молния",
    "site_header": "Молния",
    "site_brand": None,
    "site_icon": "logo/favicon.png",
    "site_logo": "logo/eng-logo.png",
    "login_logo": None,
    "site_logo_classes": "custom-logo-style",
    "copyright": 'Проект компании ООО "ЦЦ ТЭК" | cdtek.ru',
    "welcome_sign": "Добро пожаловать в Молнию",
    "related_modal_active": True,
    "show_ui_builder": False,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/admin_row_dimming.js",
    "topmenu_links": [
        {
            "name": "Мульти-рассылка молний",
            "url": "admin-lightning-multisend",
            "icon": "fas fa-bolt",
        },
        {
            "name": "Статистика молний",
            "url": "admin-statistics",
            "icon": "fas fa-chart-bar",
        },
        {
            "name": "Общая статистика",
            "url": "admin-lightnings-vs-users",
            "icon": "fas fa-chart-bar",
        },
        {
            "name": "По подразделениям",
            "url": "admin-lightnings-summary-by-departments",
            "icon": "fas fa-chart-pie",
        },
    ],
    # "hide_models": [
    #     "bot.passwordresettoken",
    # ],
    "order_with_respect_to": [
        "bot",
        "lightning",
        "organization",
        "scheduler",
        "core",
        # Телеграм бот
        "bot.telegramuser",
        "bot.telegramgroup",
        # Молния
        "lightning.lightning",
        "lightning.lightningquestion",
        "lightning.lightninganswer",
        "lightning.lightningsetting",
        "lightning.lightningread",
        "lightning.lightningtest",
        "lightning.usertestattempt",
        # Справочники
        "organization.company",
        "organization.department",
        "organization.jobtitle",
        # Планировщик
        "scheduler.schedulerlog",
        # Core
        "core.instruction",
        "core.boteventlog",
        # Админ
        "auth.user",
        "auth.group",
        # Integration
        "integration.apisettings",
    ],
    "icons": {
        # Admin
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        # Bot
        "bot": "fas fa-robot",
        "bot.telegramuser": "fas fa-user-graduate",
        "bot.telegramgroup": "fas fa-users",
        # Lightning
        "lightning": "fas fa-bolt",
        "lightning.lightning": "fas fa-bolt",
        "lightning.lightningquestion": "fas fa-question-circle",
        "lightning.lightninganswer": "fas fa-check-square",
        "lightning.lightningsetting": "fas fa-cog",
        "lightning.lightningread": "fas fa-book-reader",
        "lightning.lightningtest": "fas fa-tasks",
        "lightning.usertestattempt": "fas fa-user-check",
        # Organization
        "organization": "fas fa-sitemap",
        "organization.company": "fas fa-building",
        "organization.department": "fas fa-building",
        "organization.jobtitle": "fas fa-id-badge",
        # Scheduler
        "scheduler": "fas fa-clock",
        "scheduler.schedulerlog": "fas fa-list-alt",
        # Core
        "core.instruction": "fas fa-book",
        # Integration
        "integration.apisettings": "fas fa-cog",
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
