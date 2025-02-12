import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'django-insecure-k21axct0=2e)oh913xn$izlt#p7gf@yr-!2v$$6&4((v+51*9A'  # Replace with your actual secret key
DEBUG = True # Set to False in production

ALLOWED_HOSTS = ['mashach.pythonanywhere.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # CORS headers for frontend communication
    'main',  # Your app name
    'whitenoise.runserver_nostatic',  # Serve static files with WhiteNoise
    'rest_framework',  # Optional: If using Django Rest Framework
]

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files with WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'market_backend.urls'

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

WSGI_APPLICATION = 'market_backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
        'sql_mode': 'traditional',
         },
        'NAME': '',  # Database name
        'USER': '',  # Database username
        'PASSWORD': '',  # Database password
        'HOST': 'mashach.mysql.pythonanywhere-services.com',  # Database host address
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploaded files)
MEDIA_URL = '/media/'  # URL where uploaded files are served from
MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')  # Local filesystem path where uploaded files are stored


# Django REST Framework settings (optional)
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS settings for allowing requests from specific origins
CORS_ALLOW_ALL_ORIGINS = False  # Set this to False to use CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Example for local development
    'https://builderman.vercel.app',  # Your Vercel frontend URL
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF trusted origins (ensure CSRF protection while allowing specific origins)
CSRF_TRUSTED_ORIGINS = [
   
]

CORS_ORIGIN_WHITELIST = (
  
)
# Email settings (replace with your SMTP credentials)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587  # Port for TLS/STARTTLS
EMAIL_USE_TLS = True  # True for TLS, False for SSL
EMAIL_USE_SSL = False  # Deprecated, use EMAIL_USE_TLS instead
EMAIL_HOST_USER = 'mashachb.sider@gmail.com'
EMAIL_HOST_PASSWORD = 'msuo dnlp euge ifuj'


# Uncomment the following if you want to use console email backend for debugging
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Adjust logging and other settings as per your production needs

# Ensure the correct user model is used (if customized)
AUTH_USER_MODEL = 'main.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
