INSTALLED_APPS = (
    'auprico_auth',
    'auprico_core',
    'django.contrib.auth',
    'django.contrib.contenttypes',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "secret_key_for_testing 2"
AUTH_USER_MODEL = "auprico_auth.User"
