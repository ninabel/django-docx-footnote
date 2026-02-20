from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import zipfile
import re
import xml.etree.ElementTree as ET
from mammoth import convert_to_html

style_map = """
p[style-name='Center'] => p.align-center
p[style-name='Right']  => p.align-right
"""
def extract_alignment(file):
    """Reads document.xml from DOCX and returns a list of alignments for each paragraph."""
    alignments = []
    with zipfile.ZipFile(file) as docx:
        with docx.open("word/document.xml") as document_xml:
            tree = ET.parse(document_xml)
            root = tree.getroot()
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            for p in root.findall(".//w:body/w:p", ns):
                jc = p.find(".//w:pPr/w:jc", ns)
                if jc is not None:
                    alignments.append(jc.attrib.get(f"{{{ns['w']}}}val"))
                else:
                    alignments.append(None)
    return alignments

def add_alignment_to_html(html, alignments):
    """Adds inline text-align styles to HTML paragraphs without external libs."""
    paragraphs = re.findall(r"<p.*?>.*?</p>", html, flags=re.DOTALL)
    updated_html = html
    for p_tag, align in zip(paragraphs, alignments):
        if align in ("left", "right", "center", "both"):
            css_align = "justify" if align == "both" else align
            # Inject style attribute
            if 'style="' in p_tag:
                new_tag = re.sub(r'style="', f'style="text-align: {css_align}; ', p_tag, count=1)
            else:
                new_tag = p_tag.replace("<p", f'<p style="text-align: {css_align};"', 1)
            updated_html = updated_html.replace(p_tag, new_tag, 1)
    return updated_html

@require_http_methods(["POST"])
def docx_preview_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        alignments = extract_alignment(file)
        result = convert_to_html(file, style_map=style_map)
        html = add_alignment_to_html(result.value, alignments)
        return JsonResponse({'html': html})
    return JsonResponse({'html': ''})
