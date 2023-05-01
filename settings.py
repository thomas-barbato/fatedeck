import os
import infos

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(*k%eq*0qt90-*1(57zn-tw#-u6*=)j)f+m3jvie$kiio=#1f4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
INTERNAL_IPS = ("127.0.0.1:8000", "127.0.0.1")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
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


ROOT_URLCONF = 'urls'

# Authentication with email
AUTHENTICATION_BACKENDS = ['core.backend.authentication.EmailBackend']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,'core', 'templates/core/'),
            os.path.join(os.path.join(BASE_DIR,'core', 'templates/core/'),'panels'),
            os.path.join(os.path.join(BASE_DIR,'core', 'templates/core/'),'display'),
            os.path.join(os.path.join(BASE_DIR,'core', 'templates/core/'),'create'),],
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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DEBUG_VALUE, KEY, HOST, DB_NAME, USER, PASSWORD, PORT, CHARSET, DB_ENGINE, EMAIL = infos.getter_setting()
DATABASES = {
     'default': {
         'ENGINE': DB_ENGINE,
         'NAME': DB_NAME,
         'USER': USER,
         'PASSWORD': PASSWORD,
         'HOST': HOST,
         'PORT': PORT,
         'default-character-set': CHARSET,
         'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
         }
     }
}


"""
    JSON FIXTURES
"""
FIXTURE_DIRS = [
    BASE_DIR+'core/fixtures/pargen.json',
    BASE_DIR+'core/fixtures/cards.json',
]

AUTH_USER_MODEL = 'core.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
