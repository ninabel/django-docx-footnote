from django.shortcuts import render
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

def get_footnote_from_html(html):
    """Extracts footnotes from HTML and returns a list of footnote texts."""
    footnotes_ol_match = re.search(
    r'<ol[^>]*>(<li id="footnote-\d+"[^>]*>.*?)</ol>',
    html, re.DOTALL | re.IGNORECASE
    )
    if footnotes_ol_match:
        footnotes_html = footnotes_ol_match.group(1)
        main_content = html.replace(footnotes_ol_match.group(0), '').strip()
    else:
        main_content = html
        footnotes_html = ''
        
    return {
        'content': main_content,
        'footnotes': [
            {
                'id': match.group(2),
                'tag': match.group(1),
                'text': match.group(3).strip().replace(match.group(4), ''),
                'backref': match.group(5)
            }
            for match in re.finditer(r'<li id="(footnote-(\d+))"><p>(.*?(<a href="(#footnote-ref-\d+)">.*?</a>))</p></li>', footnotes_html, re.DOTALL)
        ]
    }

@require_http_methods(["POST"])
def docx_preview_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        alignments = extract_alignment(file)
        result = convert_to_html(file, style_map=style_map)
        html = add_alignment_to_html(result.value, alignments)
        document = get_footnote_from_html(html)
        return render(request, 'footnotes.html', document)
    return ''
