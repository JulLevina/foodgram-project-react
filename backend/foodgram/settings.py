import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', default='SUP3R-S3CR3T-K3Y-F0R-MY-PR0J3CT')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djoser',
    'api.apps.ApiConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
]

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

NUMBER_OF_RECIPES = 6

ROOT_URLCONF = 'foodgram.urls'

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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        # 'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
        # 'NAME': os.getenv('DB_NAME', default='postgres'),
        # 'USER': os.getenv('POSTGRES_USER', default='Admin'),
        # 'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='Admin_user'),
        # 'HOST': os.getenv('DB_HOST', default='db'),
        # 'PORT': os.getenv('DB_PORT', default=5432)
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/django/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static', 'django')

STATICFILES_DIRS = ['/app/data']

MEDIA_URL = '/media/django/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media', 'django')

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.v1.pagination.FoodgramPagination',
    'PAGE_SIZE': 6,

}

DJOSER = {
    'HIDE_USERS': False,
    'PERMISSIONS': {

        'user_list': ['rest_framework.permissions.IsAuthenticated'],

    },

    "SERIALIZERS": {
        "user_create": "api.v1.serializers.users.UserCreateSerializer",
        "user": "api.v1.serializers.users.UserSerializer",
        "current_user": "api.v1.serializers.users.UserSerializer",
        "user_delete": "djoser.serializers.UserSerializer",
    },
}
