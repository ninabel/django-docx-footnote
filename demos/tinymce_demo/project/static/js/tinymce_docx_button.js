document.addEventListener("DOMContentLoaded", function () {
    if (!window.tinymce) {
        return;
    }

    tinymce.PluginManager.add("docx_upload_plugin", function (editor) {
        editor.ui.registry.addButton("docx", {
            text: "DOCX",
            tooltip: "Upload DOCX",
            onAction: function () {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = ".docx";

                input.addEventListener("change", async function () {
                    if (!input.files.length) {
                        return;
                    }
                    const file = input.files[0];
                    if (file.name.split(".").pop().toLowerCase() !== "docx") {
                        alert("Please select a DOCX file");
                        return;
                    }

                    const formData = new FormData();
                    formData.append("file", file);

                    try {
                        const response = await fetch("/admin/docx-preview/", {
                            method: "POST",
                            headers: {
                                "X-Requested-With": "XMLHttpRequest",
                                "X-CSRFToken": getCookie("csrftoken"), // You need to implement getCookie},
                            },
                            body: formData,
                        });

                        if (!response.ok) {
                            throw new Error("Upload failed");
                        }

                        const text = await response.text();
                        editor.insertContent(
                            text
                        );
                    } catch (e) {
                        console.error(e);
                        alert("DOCX upload failed");
                    }
                });

                input.click();
            },
        });
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

});