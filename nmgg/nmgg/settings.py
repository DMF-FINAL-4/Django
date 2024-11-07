
# BASE_DIR 설정
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


# api 키 가져오기
import os
from dotenv import load_dotenv
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# print(f"Loaded OPENAI_API_KEY: {OPENAI_API_KEY}")

# 엘라스틱 서치 주소
from elasticsearch import Elasticsearch

CA_CERT_PATH = os.path.join(BASE_DIR, 'certs', 'http_ca.crt')

# 인증서를 사용하는 Elasticsearch 클라이언트 생성
ELASTICSEARCH = Elasticsearch(
    ['https://localhost:9200'],
    ca_certs=CA_CERT_PATH,  # 인증서 파일 경로 지정
    verify_certs=True,  # 인증서 검증 활성화
    http_auth=('admin', 'admin1234'),  # 기본 인증 정보가 필요한 경우

    timeout=30,  # 요청 타임아웃 설정
    max_retries=10,  # 최대 재시도 횟수
    retry_on_timeout=True  # 타임아웃 발생 시 재시도
)
# # 테스트용
# ELASTICSEARCH = Elasticsearch(
#     ['https://localhost:9200'],
#     timeout=30,  # 요청 타임아웃 설정
#     max_retries=10,  # 최대 재시도 횟수
#     retry_on_timeout=True,  # 타임아웃 발생 시 재시도
#     verify_certs=False,  # 인증서 검증 비활성화
#     ssl_show_warn=False,  # 인증서 경고 비활성화
# )

"""
Django settings for nmgg project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(qn)cs5&84no*&l8=0z@x%h-wn67xqo_jp$th9^)+j&tvq)(-b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'page_save',
    'summariz',
    'corsheaders', # CORS를 허용하기위해
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS를 허용하기위해
]
# CORS를 허용하기위해
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'nmgg.urls'

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

WSGI_APPLICATION = 'nmgg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
