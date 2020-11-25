from corsheaders.defaults import default_methods, default_headers

SECRET_KEY = '8g#mt#p!f^+xy-n6p+64n&cm92b61zi6_9q097(3e0o)xntbt_'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'rest_framework',
    'corsheaders',
    'django_rest_passwordreset',
    'django_cron',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'safedelete',
    'drf_yasg'
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.http.middlewares.ResetPasswordAuthMiddleware',
]

ROOT_URLCONF = 'ella-admin.urls'

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

WSGI_APPLICATION = 'ella-admin.wsgi.application'

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
    {
        'NAME': 'api.validators.DifferentPasswordValidator'
    }
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    )
}

PASSWORD_HASHERS = (
    'api.auth.hashers.CustomBCryptSHA256PasswordHasher',
)

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login',
    'LOGOUT_URL': '/admin/logout'
}

CORS_ALLOW_METHODS = default_methods
CORS_ALLOW_HEADERS = default_headers + (
    'access-control-expose-headers',
    'Access-Control-Allow-Origin',
    'cache-control',
    'if-none-match',
)
CORS_EXPOSE_HEADERS = ()
CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = 'api.User'

DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 0.5
RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITHOUT_PASSWORD = {'months': 1}
RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITH_PASSWORD = {'hours': DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME}

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CRON_CLASSES = [
    'api.jobs.ClearPasswordResetTokenJob'
]

DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE = True

PASSWORD = {
    'live_time_days': 90
}
