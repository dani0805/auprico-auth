INSTALLED_APPS = (
    'auprico_auth',
    'auprico_core',
)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "secret_key_for_testing 2"