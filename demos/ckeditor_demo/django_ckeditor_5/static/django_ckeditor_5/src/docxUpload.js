import { Plugin } from '@ckeditor/ckeditor5-core';
import { ButtonView } from '@ckeditor/ckeditor5-ui';
import { IconImportExport } from '@ckeditor/ckeditor5-icons';

export default class DocxUpload extends Plugin {
    static get pluginName() {
        return 'docxUpload';
    }

    init() {
        const editor = this.editor;

        // Register toolbar button
        editor.ui.componentFactory.add('docxUpload', locale => {
            const view = new ButtonView(locale);

            view.set({
                label: 'DOCX Upload',
                icon: IconImportExport,
                tooltip: true
            });

            // Button click handler
            this.listenTo(view, 'execute', async () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.docx';
                document.body.appendChild(input);
                input.click();
                document.body.removeChild(input);

                input.onchange = async () => {
                    const file = input.files[0];
                    if (!file) return;
                    if (file.name.split('.').pop().toLowerCase() !== 'docx') {
                        alert('Please select a DOCX file');
                        return;
                    }

                    const formData = new FormData();
                    formData.append('file', file);

                    try {
                        const response = await fetch('/admin/docx-preview/', {
                            method: 'POST',
                            headers: { 
                                'X-Requested-With': 'XMLHttpRequest',
                                'X-CSRFToken': this._getCsrfToken()
                            },
                            body: formData,
                        });

                        const text = await response.text();

                        // Insert uploaded DOCX
                        editor.setData(text);
                    } catch (e) {
                        console.error('DOCX upload failed:', e);
                    }
                };
            });

            return view;
        });
    }


    _getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}
