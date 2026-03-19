from django.contrib import admin
from django import forms
from library.models import Document

from django_ckeditor_5.widgets import CKEditor5Widget


class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "content"]
        widgets = {
            "content": CKEditor5Widget(config_name="default"),
        }


# register Document model with custom admin form and widget for docx upload
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm

    # class Media:
    #     js = (
    #         "js/docx-upload-plugin.js",
    #     )


# register Document model with custom admin form
admin.site.register(Document, DocumentAdmin)
