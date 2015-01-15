"""
Django settings for WC2048 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# keep debug intialisation at the top of the file so that we always know if we're in debug or production
msg = "isDebug file is expected to consist of a single charcter 0 or 1"
try:
    with open("isDebug") as isDebug:
        isDebug = isDebug.readlines()[0][0]
        if isDebug == "0":
            DEBUG = False
        elif isDebug == "1":
            DEBUG = True
        else:
            raise Exception(msg)
except Exception as e:
    #raise Exception(e.message +)
    #print e.message
    raise Exception(e.message + msg)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# declaring some global variables
# this pretty much is a setting. 
OUR_WALLET = '1Li2pXrVbuM4ga3HsoA6RPLSQPfrxYBJKA'

OUR_URL = os.getenv('EXTERNALIP', None) 
if OUR_URL == None and not DEBUG:
    raise Exception("blowing up -- need correct external IP of the server")
if OUR_URL == None and DEBUG:
    OUR_URL = "127.0.0.1" # that's an obviously dummy address.

GAME_COST = 0.0005 #setting the minimum amount the ai will allow for just now.

ALLOWED_HOSTS = [
    "*",
]

# SECURITY WARNING: keep the secret key used in production secret!
if not DEBUG:
    try:
        SECRET_KEY
    except NameError: 
        import binascii
        keyassigned = "randomly generated key" 
        with open("/dev/urandom", 'rb') as f:
            SECRET_KEY = binascii.hexlify(f.read(32))
if DEBUG:
    SECRET_KEY = '1337'

TEMPLATE_DEBUG = True

TEMPLATE_DIRS=(
    os.path.join(BASE_DIR, 'templates'),
)

# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    #'django.contrib.sessions',
    #'django.contrib.messages',
    'website',
)

if DEBUG:
    INSTALLED_APPS += ('django.contrib.staticfiles',)


MIDDLEWARE_CLASSES = (
    #'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'WC2048.urls'

WSGI_APPLICATION = 'WC2048.wsgi.application'

#CSRF_COOKIE_SECURE = False
#SESSION_COOKIE_SECURE = False
# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        #'ATOMIC_REQUESTS': True
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-uk'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
if DEBUG:
    import os
    STATIC_ROOT = 'staticfiles'
    STATIC_URL = '/static/'

    STATICFILES_DIRS = (
        os.path.join(BASE_DIR, 'static'),
    )

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )
