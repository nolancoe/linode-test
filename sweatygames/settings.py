"""
Django settings for sweatygames project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-y-t1^@$njd5$mf0sino6oclos9(@^+2d&se45_#=hexpo6=ujd'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '198.58.101.181']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    #MyApps
    'users',
    'core',
    'teams',
    'matches',
    'messaging',
    'duos_teams',
    'duos_matches',

    #3rd Party Apps
    'django_countries',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.steam',
    'allauth.socialaccount.providers.battlenet',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.twitch',
    "anymail",


]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'users.custom_middleware.BanCheckMiddleware',
    'users.custom_middleware.RestrictAdminMiddleware',
    
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'sweatygames.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'core.context_processors.matches_context',
                'core.context_processors.dispute_proofs_context',
                'core.context_processors.direct_challenge_context',
                'core.context_processors.message_context',
                'core.context_processors.team_invites_context',
                'core.context_processors.duos_team_invites_context',
                'core.context_processors.duos_matches_context',
                'core.context_processors.direct_duos_challenge_context',
                'core.context_processors.duos_dispute_proofs_context',

            ],
        },
    },
]


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',


)

EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"


ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True



ANYMAIL = {
    "SENDINBLUE_API_KEY": "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",
}

DEFAULT_FROM_EMAIL = 'Sweaty Games <nolancoe@live.com>'

ACCOUNT_SIGNUP_REDIRECT_URL = '/request_verification'

# Add Social Account Providers
SOCIALACCOUNT_PROVIDERS = {
    'openid': {
        'Steam': {
            'SERVERS': [
                {
                    'client_id': '3FD78E9A303947AD32F4BB487FFCC840',
                },
            ],
        },
    },
    'battlenet': {
        'REGION': 'us',
        'SERVERS': [
            {
                'client_id': '3587dd4eaf5c4e5e9dfbd631e9a1e11f',
                'secret': 'HIL3w6jQivuRZbsT3Qw8PHLQmtJFXrz9',
                'redirect_uris': ['http://localhost:8000/accounts/battlenet/login/callback/'],
            },
        ],
    },
    'discord': {
        'DISCORD': {
            'client_id': '1179189466389299321',
            'secret': 'f9yqlUbU5FReA4yUe7tH-zCxxEkxklgH',
            'SCOPE': ['identify', 'email'],  # Adjust scopes as needed
            'METHOD': 'oauth2',
            'redirect_uris': ['http://localhost:8000/accounts/discord/login/callback/'],
        },
    },
    'twitch': {
        'METHOD': 'oauth2',
        'CLIENT_ID': '7zbtqqijo5f659txd0hdd8ef9u0qtq',
        'CLIENT_SECRET': 'lh2xod4ky76lslevhtn22tspbc3hgm',
        'AUTH_PARAMS': {'access_type': 'online'},
        'INIT_PARAMS': {'redirect_uri': 'http://localhost:8000/accounts/twitch/login/callback/'},
    },

}


# Redirect URL after login (You can change this according to your app)
LOGIN_REDIRECT_URL = '/'



# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.Profile'
# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
