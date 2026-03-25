INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.admin",
    "django_docx_footnote",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # in-memory: fast, no files left behind
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["django_docx_footnote/templates"],
        "APP_DIRS": False,
        "OPTIONS": {"context_processors": []},
    }
]
ROOT_URLCONF = (
    "tests.conftest_urls"  # points to the URL patterns defined in conftest_urls.py
)
LOGIN_URL = "/login/"  # tells staff_member_required where to redirect
USE_TZ = False  # avoid timezone issues in tests
