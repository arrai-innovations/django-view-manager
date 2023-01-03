# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/stable/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/stable/ref/settings/#site-id
SITE_ID = 1


# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "django_view_manager_db",  # Only needed during setup of apps and migrations.  Db file is not committed.
    }
}


# DEFAULT_AUTO_FIELD
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/releases/3.2/#customizing-type-of-auto-created-primary-keys
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# APPS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#installed-apps
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "tests.animals",
    "tests.employees",
    "tests.food",
    "django_view_manager.utils",
]


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/stable/ref/settings/#logging
# See https://docs.djangoproject.com/en/stable/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}


# TEST_RUNNER
# https://docs.djangoproject.com/en/stable/ref/settings/#test-runner
TEST_RUNNER = "tests.test_runner.TestRunner"
