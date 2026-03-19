import { Plugin, ButtonView, icons } from 'ckeditor5';

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
                icon: icons.importExport,
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
                        const response = await fetch('/admin/docx-upload/', {
                            method: 'POST',
                            headers: { 'X-Requested-With': 'XMLHttpRequest' },
                            body: formData,
                        });

                        const text = await response.text();

                        // Insert link to uploaded DOCX
                        editor.execute('insertContent',
                            { html: text }
                        );
                    } catch (e) {
                        console.error('DOCX upload failed:', e);
                    }
                };
            });

            return view;
        });
    }


    _getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}
