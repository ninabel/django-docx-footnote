import io
import zipfile
import xml.etree.ElementTree as ET


NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def build_docx(alignments: list) -> io.BytesIO:
    """Return an in-memory DOCX file with one paragraph per alignment value.
    Pass None for a paragraph with no <w:jc> element."""
    root = ET.Element(f"{{{NS}}}document")
    body = ET.SubElement(root, f"{{{NS}}}body")
    for align in alignments:
        p = ET.SubElement(body, f"{{{NS}}}p")
        if align is not None:
            pPr = ET.SubElement(p, f"{{{NS}}}pPr")
            jc = ET.SubElement(pPr, f"{{{NS}}}jc")
            jc.set(f"{{{NS}}}val", align)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", xml_bytes)
    buf.seek(0)
    return buf


# HTML fixtures that match mammoth's compact output (no newlines inside <ol>)
SINGLE_FN_HTML = (
    '<p>Main content.<sup id="footnote-ref-1"><a href="#footnote-1">1</a></sup></p>'
    "<ol>"
    '<li id="footnote-1"><p>First footnote.<a href="#footnote-ref-1">back</a></p></li>'
    "</ol>"
)

MULTI_FN_HTML = (
    '<p>Text<sup id="footnote-ref-1"><a href="#footnote-1">1</a></sup>'
    '<sup id="footnote-ref-2"><a href="#footnote-2">2</a></sup></p>'
    "<ol>"
    '<li id="footnote-1"><p>First footnote.<a href="#footnote-ref-1">back</a></p></li>'
    '<li id="footnote-2"><p>Second footnote.<a href="#footnote-ref-2">back</a></p></li>'
    "</ol>"
)

NO_FN_HTML = "<p>No footnotes here.</p>"

DOCX_PREVIEW_URL = "/admin/docx-preview/"
