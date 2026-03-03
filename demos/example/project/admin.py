from django.contrib import admin
from django import forms
from library.models import Document
from django_docx_footnote.admin.widgets import DocxUploadWidget


class DocumentAdminForm(forms.ModelForm):
    upload_file = forms.FileField(
        required=False,
        widget=DocxUploadWidget(attrs={"accept": ".docx", "HtmlField": "content"}),
        help_text="Upload a .docx file to extract text",
    )

    class Meta:
        model = Document
        fields = ["title", "content"]


class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm


admin.site.register(Document, DocumentAdmin)
