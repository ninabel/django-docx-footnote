# Django DOCX with footnotes Uploader 

Django admin plugin that lets you upload ```.docx``` files, extract formatted text with custom footnote handling, and store the result as clean HTML in a model ```TextField```.

## Features
* **Django admin integration** - uploads ```.docx``` files directly from the admin interface

* **Custom footnote formatting** - converts ```.docx``` files footnotes to styled HTML using a django-like template

* **Clean HTML output** - removes unnecessary inline styles from Word-generated markup

* **Seamless model integration** - stores processed HTML in a standard TextField

## Requirements

- Python 3.9+ (CKEditor demo requires Python 3.11+)
- Django 3.2+


## Installation

**Option 1: Copy into your project** 

Copy ```django_docx_footnote/``` directory from this repository into your Django project.


**Option 2: Install from Git**

```bash
pip install git+https://github.com/ninabel/django-docx-footnote.git
```

**Configure Django**

Add "django_docx_footnote" to INSTALLED_APPS:
```python
# settings.py
INSTALLED_APPS = [
    ...,
    "django_docx_footnote",
    ...
]
```

Register the preview endpoint **before** admin urls:
```python
# urls.py
urlpatterns = [
    path("admin/docx-preview/", docx_preview_view, name="docx_preview"),
    path("admin/", admin.site.urls),
    ...
]
```

## Usage

### Template requirement

Create a ```footnotes.html``` template that defines how footnotes should be rendered.
This template should match your project’s styling.

Posting DOCX file to ```admin/docx-preview/``` URL you will obtain proccessed HTML. See examples for more details.

### Basic Admin Integration

Use ```DocxUploadWidget``` to add **Upload** button to your basic Django admin form for model with a TextField.

```python
# admin.py

from django_docx_footnote.admin.widgets import DocxUploadWidget


class DocumentAdminForm(forms.ModelForm):
    upload_file = forms.FileField(
        required=False,
        widget=DocxUploadWidget(attrs={"accept": ".docx", "HtmlField": "content"}),
        help_text="Upload a .docx file to extract text",
    )

```
Attribute **HtmlField** must match the name of the model field where HTML will be stored.

Full example: ```demos/example/project/admin.py```

### TinyMCE Integration

1. Install ```django-tinymce``` extansion 
2. Create custom javascript plugin:
```demos/tinymce_demo/project/static/js/tinymce_docx_button.js```
3. Add a custom DOCX upload button to TinyMCE toolbar config
```python
# settings.py
TINYMCE_DEFAULT_CONFIG = {
    ...
    "plugins": "lists link image preview docx_upload_plugin",
    "toolbar": "docx undo redo | ... ",
    ...
}
```

### CKEditor 5 Integration

**Note:** Python 3.11+ required

1. Clone and integrate **django-ckeditor-5** extension
2. Add the custom plugin to its JS source: 
```demos/ckeditor_demo/django_ckeditor_5/static/django_ckeditor_5/src/docxUpload.js```
3. Registrate plugin:
```javascript
# ckeditor.js
# import list
...
import DocxUpload from './docxUpload.js';
...
ClassicEditor.builtinPlugins = [
    ...
    DocxUpload,
]
```
4. Rebuild: 
```bash
npm install && npm run prod
``` 
(or use ```yarn```)

4. Run 
```bash
python manage.py collectstatic
```

### API Endpoint
```POST /admin/docx-preview/```

Upload a .docx file and receive processed HTML.

Used internally by widgets and editor integrations, but can also be called manually.

## Demo Projects

Build and run all demos via Docker:

1. **Build wheel** 
   ```bash
   uv build --wheel
   ```

2. **Run demos**:
   ```bash
   docker compose up --build
   ```

   Available at:
   
   - http://localhost:8001 - basic example
   - http://localhost:8002 - TinyMCE integration 
   - http://localhost:8003 - CKEditor integration


## Notes & Limitations

* Only .docx files are supported.
* Output depends on your footnotes.html template.
* Complex Word styling may not fully translate to clean HTML.

## Contributing

Issues and pull requests are welcome!
