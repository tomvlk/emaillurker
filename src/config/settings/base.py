"""Base settings shared by all environments"""
import os
import datetime

from django.conf.global_settings import *
from config.settings import local

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

TMP_DIR = os.path.join(BASE_DIR, 'tmp')
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
TEST_DIR = os.path.join(os.path.dirname(BASE_DIR), 'src', 'test')
DOCS_ROOT = os.path.join(BASE_DIR, '../docs/build/html')

INTERNAL_IPS = (
	'127.0.0.1',
)
ALLOWED_HOSTS = local.ALLOWED_HOSTS

try:
	os.makedirs(TMP_DIR)
except Exception:
	pass

if not hasattr(local, 'AUTHENTICATION'):
	raise Exception('Local configuration should contain AUTHENTICATION entry!')

# Generic
TIME_ZONE = 'UTC'

USE_TZ = True
USE_I18N = True
USE_L10N = True

LANGUAGE_CODE = 'en-en'

SECRET_KEY = local.SECRET_KEY
USER_API_KEYS = bool(local.USER_API_KEYS)

if SECRET_KEY == 'changeme':
	print('YOU SHOULD CHANGE YOUR SECRET KEY!!!')


####
# Mail Server Settings
####
SMTPD_ADDRESS = getattr(local, 'SMTPD_ADDRESS', '0.0.0.0')
SMTPD_PORT = getattr(local, 'SMTPD_PORT', 1025)

# Mail Forwarding policy and settings.
FORWARDING = local.FORWARDING
FORWARDING_ENABLED = bool(FORWARDING['enabled'])
FORWARDING_AUTO = bool(FORWARDING['automatically'])

if FORWARDING_ENABLED and FORWARDING['method'] == 'smtp':
	EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
	EMAIL_HOST = FORWARDING['smtp']['host']
	EMAIL_PORT = FORWARDING['smtp']['port']
	EMAIL_TIMEOUT = FORWARDING['smtp']['timeout']

	if FORWARDING['smtp']['authentication']['enabled']:
		EMAIL_HOST_USER = FORWARDING['smtp']['authentication']['username']
		EMAIL_HOST_PASSWORD = FORWARDING['smtp']['authentication']['password']

	EMAIL_USE_TLS = FORWARDING['smtp']['use_tls']
	EMAIL_USE_SSL = FORWARDING['smtp']['use_ssl']
	EMAIL_SSL_CERTFILE = FORWARDING['smtp']['ssl_certfile']
	EMAIL_SSL_KEYFILE = FORWARDING['smtp']['ssl_keyfile']
else:
	EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'


# Cleanup of old messages
CLEANUP = False
CLEANUP_AFTER = None

if type(getattr(local, 'CLEANUP_AFTER', None)) is datetime.timedelta:
	CLEANUP = True
	CLEANUP_AFTER = local.CLEANUP_AFTER


####
# Apps
####
INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.humanize',
	'django_extensions',
	'stronghold',
	'crispy_forms',
	'material',
	'material.frontend',
	'rest_framework',
	'rest_framework.authtoken',
	'compressor',
	'corsheaders',
	'docs',
]

# Add app for social login.
if 'social' in local.AUTHENTICATION and type(local.AUTHENTICATION['social']) is dict:
	INSTALLED_APPS.append('social_django')

# Add source apps
INSTALLED_APPS += [
	'apps.core.apps.CoreConfig',
	'apps.accounts.apps.AccountsConfig',

	'apps.mails.apps.MailsConfig',
	'apps.filters.apps.FiltersConfig',
	'apps.api.apps.ApiConfig',
]

####
# Base Settings and content.
####
ROOT_URLCONF = 'config.urls'
COMPRESS_ENABLED = True

LOGIN_URL = 'accounts:login'
LOGOUT_URL = 'accounts:logout'
LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'accounts.User'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

WSGI_APPLICATION = 'wsgi.application'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

####
# Middleware
####
# Add social processors
SOCIAL_ENABLED = False
if 'social' in local.AUTHENTICATION and 'enabled' in local.AUTHENTICATION['social'] and local.AUTHENTICATION['social'][
	'enabled']:
	SOCIAL_ENABLED = True

CRISPY_TEMPLATE_PACK = 'bootstrap3'

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',

	'corsheaders.middleware.CorsMiddleware',
	'stronghold.middleware.LoginRequiredMiddleware',
	'apps.accounts.middleware.SocialAuthExceptionMiddleware',
]

####
# Authentication and security
####
CORS_ORIGIN_ALLOW_ALL = True

GRAPPELLI_ADMIN_TITLE = 'Mail Lurker, Mail catcher for large environments.'

STRONGHOLD_DEFAULTS = True
STRONGHOLD_PUBLIC_URLS = [
	r'^/login/.*$',
	r'^/complete/.*$',
	r'^/core/preference$',

	r'^/api/.*$',
]

# If read-only is enabled, exempt the root.
if 'allow_readonly' in local.AUTHENTICATION and local.AUTHENTICATION['allow_readonly']:
	STRONGHOLD_PUBLIC_URLS += [
		r'^/mails/.*$',
		r'^/filters/.*$',
		r'^/$'
	]

AUTHENTICATION_BACKENDS = (
	'django.contrib.auth.backends.ModelBackend',
)

# Add social backends.
SOCIAL_BACKENDS = list()
if SOCIAL_ENABLED and 'backends' in local.AUTHENTICATION['social']:
	AUTHENTICATION_BACKENDS += local.AUTHENTICATION['social']['backends']
	SOCIAL_BACKENDS = local.AUTHENTICATION['social']['backends']

# Add default social options
if SOCIAL_ENABLED:
	SOCIAL_AUTH_STRATEGY = 'social_django.strategy.DjangoStrategy'
	SOCIAL_AUTH_STORAGE = 'social_django.models.DjangoStorage'

	SOCIAL_AUTH_PIPELINE = (
		'social_core.pipeline.social_auth.social_details',
		'social_core.pipeline.social_auth.social_uid',
		'social_core.pipeline.social_auth.auth_allowed',
		'social_core.pipeline.social_auth.social_user',
		'social_core.pipeline.social_auth.associate_by_email',
		'social_core.pipeline.user.get_username',
		'social_core.pipeline.user.create_user',
		'social_core.pipeline.social_auth.associate_user',
		'social_core.pipeline.social_auth.load_extra_data',
		'social_core.pipeline.user.user_details',
	)

	SOCIAL_AUTH_DISCONNECT_PIPELINE = (
		'social_core.pipeline.disconnect.get_entries',
		'social_core.pipeline.disconnect.revoke_tokens',
		'social_core.pipeline.disconnect.disconnect'
	)

# Add social pipelines
if SOCIAL_ENABLED and 'pipelines' in local.AUTHENTICATION['social']:
	SOCIAL_AUTH_PIPELINE = local.AUTHENTICATION['social']['pipelines']

# Add custom social options
if SOCIAL_ENABLED and 'options' in local.AUTHENTICATION['social']:
	locals().update(local.AUTHENTICATION['social']['options'])

AUTH = local.AUTHENTICATION
####
# Template and cache
####
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

				'apps.core.context.add_global_context',
				'apps.filters.context.add_global_context',
				'apps.mails.context.add_global_context',
				'social_django.context_processors.login_redirect',
				'social_django.context_processors.backends',
			],
		},
	},
]

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	'compressor.finders.CompressorFinder',
)

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
		'LOCATION': 'django_cache',
	}
}

####
# Database settings.
####
DATABASES = local.DATABASES

####
# API
####
REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',
		'rest_framework.renderers.BrowsableAPIRenderer',
	),
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework.authentication.TokenAuthentication',
		'rest_framework.authentication.SessionAuthentication',
	)
}

####
# TEST
####
if getattr(local, 'TEST', False):
	TEST = True
	TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
	TEST_APPS = (
		'apps.accounts',
		'apps.api',
		'apps.core',
		'apps.filters',
		'apps.mails'
	)

	NOSE_ARGS = [
		'--with-coverage',
		'--cover-package={}'.format(','.join(TEST_APPS)),
		'--cover-branches',
	]

####
# OVERRIDES
####
try:
	from .overrides import *
except ImportError as e:
	pass
