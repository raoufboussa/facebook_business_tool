"""
Django settings for connect_api project.

Generated by 'django-admin startproject' using Django 2.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g1j@9%kwwih2z0!!$=5m^a*75k%zt^-k(wo*a-o&l9qon)#p)s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATE_INPUT_FORMATS = ['%d-%m-%Y']
# Application definition

INSTALLED_APPS = [
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'facebook_business',
    'facebook_auth',
    'rest_framework',
    'FacebookOAuth',
    'pseudoAPI',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',

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

ROOT_URLCONF = 'connect_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates"),os.path.join(BASE_DIR, 'templates/account'),os.path.join(BASE_DIR, 'templates/socialaccount')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'connect_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'connectAPI',
        'USER': 'postgres',
        'PASSWORD': 'lakamoura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/staticfiles/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]

MEDIA_URL = '/media/img/'

MEDIA_ROOT = os.path.join(BASE_DIR,"media/img")

STATIC_ROOT = os.path.join(BASE_DIR, "static")

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',

)

SOCIALACCOUNT_QUERY_EMAIL = True    

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

SOCIAL_AUTH_FACEBOOK_KEY = '3230373573704000'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET ='0e51c739872e518f388fbf1439b6d7e7' #app key

# ACCOUNT_ADAPTER ="allauth.account.adapter.DefaultAccountAdapter"
# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS =True
# ACCOUNT_AUTHENTICATION_METHOD ="username" | "email" | "username_email"
# ACCOUNT_CONFIRM_EMAIL_ON_GET (=False)
# ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL =settings.LOGIN_URL
# ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL (=None)
# ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS (=3)
# ACCOUNT_EMAIL_CONFIRMATION_HMAC (=True)
# ACCOUNT_DEFAULT_HTTP_PROTOCOL (=”http”)

ACCOUNT_EMAIL_REQUIRED=True
ACCOUNT_USERNAME_REQURIED=True

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'rboussa16@gmail.com'
SERVER_EMAIL = 'rboussa16@gmail.com'
EMAIL_HOST_PASSWORD = 'LAKAMOURAbisou1995'


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

SOCIALACCOUNT_PROVIDERS = \
    {'facebook':
       {'METHOD': 'oauth2',
        'SCOPE': ['email','user_events', 'public_profile', 'user_friends','user_posts','user_likes','manage_pages','read_insights','ads_read'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': lambda request: 'kr_KR',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.4'}
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

TIMEOUT = None
ACCOUNT_LOGOUT_REDIRECT_URL ="/"
SIGNUP_REDIRECT_URL = '/account_login'
LOGIN_REDIRECT_URL = '/home'
LOGIN_URL = "/accounts/login"

SITE_ID = 1