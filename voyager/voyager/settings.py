"""
Django settings for voyager project.

Generated by 'django-admin startproject' using Django 2.2.5.

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
SECRET_KEY = 'e83dv9no3+9j%i^4en2&lbdj_vq0i9k!)6*b0cl=8eoxn28_ku'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#comentario
#comentario2
#comentario3
#comentario4

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'root.apps.RootConfig',
    'tracking.apps.TrackingConfig',
    'reportes.apps.ReportesConfig',
    'ventas.apps.VentasConfig',
    'cuentas.apps.CuentasConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'flags',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'flags.middleware.FlagConditionsMiddleware',
]

ROOT_URLCONF = 'voyager.urls'

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
            ],
        },
    },
]

FLAGS = {

    'Modulo_Cotizaciones': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Catalogo': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Ingresar_Muestra': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Ordenes_Internas': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Usuarios': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Exportar_Datos': [
        {'condition': 'boolean', 'value': True},
    ],
    'Modulo_Empresas': [
        {'condition': 'boolean', 'value': True},
    ],
    'Editar_Perfil': [
        {'condition': 'boolean', 'value': True},
    ],
    'Importar_Analisis': [
        {'condition': 'boolean', 'value': True},
    ],
    'FLAG_WITH_REQUIRED_CONDITIONS': []
}
#
WSGI_APPLICATION = 'voyager.wsgi.application'
LOGIN_REDIRECT_URL = '/cuentas/home/'
LOGOUT_REDIRECT_URL = '/cuentas/login/'
LOGIN_URL = '/cuentas/login'
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'voyager',
        'USER': 'hockey',
        'PASSWORD': 'lalocura',
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

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

file_API_KEY=open("./API_KEY_recover_password.txt",'rb')
SENDGRID_API_KEY = file_API_KEY.read().decode('ascii')

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'not-reply@internationalfoodscontrol.com'