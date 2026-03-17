from django.contrib import admin
from django import forms
from library.models import Document

from tinymce.widgets import TinyMCE


class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "content"]
        widgets = {
            "content": TinyMCE(attrs={"cols": 80, "rows": 30}),
        }


# register Document model with custom admin form and widget for docx upload
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm


admin.site.register(Document, DocumentAdmin)
print("Registered Document model with custom admin form and widget for docx upload")
