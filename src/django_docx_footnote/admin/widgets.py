# admin widget for upload docx file and convert it to html with footnotes
from django import forms

class DocxUploadWidget(forms.ClearableFileInput):
    template_name = 'widgets/docx_upload_widget.html'

