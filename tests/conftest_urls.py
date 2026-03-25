from django.contrib import admin
from django.urls import path
from django_docx_footnote.admin.views import docx_preview_view

from .conftest import DOCX_PREVIEW_URL

urlpatterns = [
    path(DOCX_PREVIEW_URL, docx_preview_view, name="docx_preview"),
    path("admin/", admin.site.urls),
]
