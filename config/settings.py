from email.policy import default
from pathlib import Path
from decouple import config, Csv
from django.utils.translation import gettext_lazy as _
BASE_DIR = Path(__file__).resolve().parent.parent
from django.contrib import messages
from django.templatetags.static import static
from django.urls import reverse_lazy


SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition
# ----------------------------------------------------------------------------------------------------------------------
INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'unfold.contrib.import_export',
    'unfold.contrib.guardian',
    'unfold.contrib.simple_history',
    'unfold.contrib.location_field',
    'unfold.contrib.constance',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'ui',
    'core.apps.CoreConfig',

    # apps...
    'apps.main.apps.MainConfig',
    'apps.dashboard.teacher.apps.TeacherConfig',
    'apps.dashboard.learner.apps.LearnerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS += ['django_browser_reload']
    MIDDLEWARE += [
        'django_browser_reload.middleware.BrowserReloadMiddleware',
    ]

AUTH_USER_MODEL = 'core.User'
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'ui/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# ----------------------------------------------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_USER_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# Password validation
# ----------------------------------------------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# ----------------------------------------------------------------------------------------------------------------------
LANGUAGES = (
    ('kk', _('Kazakh')),
    ('ru', _('Russian')),
    ('en', _('English')),
)

LOCALE_PATHS = [
    BASE_DIR / 'locales'
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

LANGUAGE_SESSION_KEY = 'django_language'


# Static files (CSS, JavaScript, Images)
# ----------------------------------------------------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / 'ui/static'
]


# Templates settings
# ----------------------------------------------------------------------------------------------------------------------
TAILWIND_APP_NAME = 'ui'

# Messages
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

MESSAGE_TAGS = {
    messages.SUCCESS: 'text-emerald-600',
    messages.WARNING: 'text-amber-500',
    messages.INFO: 'text-brand',
    messages.ERROR: 'text-destructive',
}


# Authentication settings
# ----------------------------------------------------------------------------------------------------------------------
LOGIN_URL = 'main:login'
LOGIN_REDIRECT_URL = 'main:post-auth-redirect'
LOGOUT_REDIRECT_URL = 'main:home'


# Unfold settings
# ----------------------------------------------------------------------------------------------------------------------
# Unfold settings
# ----------------------------------------------------------------------------------------------------------------------
UNFOLD = {
    'SITE_TITLE': config('SITE_NAME'),
    'SITE_HEADER': config('SITE_NAME'),
    'SITE_SUBHEADER': _('Dashboard'),

    'LOGIN': {
        'image': lambda request: static('images/admin-hero.svg'),
        'title': _('Dashboard'),
    },

    'SITE_URL': '/',
    'SITE_ICON': lambda request: static('images/icon.svg'),
    'SITE_SYMBOL': 'speed',
    'SITE_FAVICONS': [
        {
            'rel': 'icon',
            'sizes': '32x32',
            'type': 'image/svg+xml',
            'href': lambda request: static('images/icon.svg'),
        },
    ],
    'SHOW_LANGUAGES': True,

    'SITE_DROPDOWN': [
        {
            'icon': 'home',
            'title': _('Administration'),
            'link': config('ADMIN_URL'),
        },
        {
            'icon': 'open_in_new',
            'title': _('Website'),
            'link': config('WEBSITE_URL'),
            'attrs': {
                'target': '_blank',
            },
        },
    ],

    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': True,

        'navigation': [
            {
                'items': [
                    {
                        'title': _('Dashboard'),
                        'icon': 'dashboard',
                        'link': reverse_lazy('admin:index'),
                        'badge': '3',
                        'badge_variant': 'info',
                        'badge_style': 'solid',
                        'permission': lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                'title': _('Account'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Users'),
                        'icon': 'people',
                        'link': reverse_lazy('admin:core_user_changelist'),
                    },
                    {
                        'title': _('Classrooms'),
                        'icon': 'user_attributes',
                        'link': reverse_lazy('admin:core_classroom_changelist'),
                    },
                    # ...
                ],
            },
        ],
    },

    'BORDER_RADIUS': '12px',
    'COLORS': {
        'primary': {
            '50': '#eef2ff',
            '100': '#e0e7ff',
            '200': '#c7d2fe',
            '300': '#a5b4fc',
            '400': '#818cf8',
            '500': "#6366f1",
            '600': '#4f46e5',
            '700': '#4338ca',
            '800': '#3730a3',
            '900': '#312e81',
            '950': '#1e1b4b',
        },
    },
}
