"""
pytest tests for django_docx_footnote.admin.views.py
====================================================

Requirements:
    pip install pytest pytest-django mammoth

Run:
    pytest test_views.py -v
"""

from unittest.mock import MagicMock, patch

from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile

import pytest

from django_docx_footnote.admin.views import (
    add_alignment_to_html,
    extract_alignment,
    get_footnote_from_html,
    docx_preview_view,
)

from .conftest import (
    build_docx,
    SINGLE_FN_HTML,
    MULTI_FN_HTML,
    NO_FN_HTML,
    DOCX_PREVIEW_URL,
)

# ---------------------------------------------------------------------------
# extract_alignment
# ---------------------------------------------------------------------------


class TestExtractAlignment:
    def test_returns_one_entry_per_paragraph(self):
        assert len(extract_alignment(build_docx(["center", "right", None]))) == 3

    def test_correct_alignment_values(self):
        assert extract_alignment(build_docx(["center", "right", "left"])) == [
            "center",
            "right",
            "left",
        ]

    def test_none_when_jc_element_is_absent(self):
        assert extract_alignment(build_docx([None])) == [None]

    def test_empty_document_returns_empty_list(self):
        assert extract_alignment(build_docx([])) == []

    def test_mixed_present_and_absent(self):
        assert extract_alignment(build_docx(["center", None, "right"])) == [
            "center",
            None,
            "right",
        ]

    def test_both_is_returned_verbatim(self):
        # "both" is Word XML for justified – returned as-is; CSS mapping happens later
        assert extract_alignment(build_docx(["both"])) == ["both"]

    def test_single_left_paragraph(self):
        assert extract_alignment(build_docx(["left"])) == ["left"]


# ---------------------------------------------------------------------------
# add_alignment_to_html
# ---------------------------------------------------------------------------


class TestAddAlignmentToHtml:
    @pytest.mark.parametrize(
        "align,expected_css",
        [
            ("center", "text-align: center"),
            ("right", "text-align: right"),
            ("left", "text-align: left"),
            ("both", "text-align: justify"),  # "both" maps to justify
        ],
    )
    def test_valid_alignment_injected(self, align, expected_css):
        result = add_alignment_to_html("<p>Hello</p>", [align])
        assert expected_css in result

    def test_both_does_not_produce_text_align_both(self):
        result = add_alignment_to_html("<p>Hello</p>", ["both"])
        assert "text-align: both" not in result

    def test_none_alignment_leaves_paragraph_unchanged(self):
        html = "<p>Hello</p>"
        assert add_alignment_to_html(html, [None]) == html

    def test_unknown_value_not_applied(self):
        assert "text-align" not in add_alignment_to_html("<p>Hello</p>", ["unknown"])

    def test_multiple_paragraphs_aligned_individually(self):
        html = "<p>One</p><p>Two</p><p>Three</p>"
        result = add_alignment_to_html(html, ["left", None, "right"])
        assert "text-align: left" in result
        assert "text-align: right" in result

    def test_existing_style_attribute_preserved(self):
        html = '<p style="color: red;">Hello</p>'
        result = add_alignment_to_html(html, ["center"])
        assert "color: red" in result
        assert "text-align: center" in result

    def test_more_paragraphs_than_alignments_does_not_raise(self):
        # zip() truncates to the shorter list – remaining paragraphs untouched
        html = "<p>One</p><p>Two</p>"
        result = add_alignment_to_html(html, ["center"])
        assert "text-align: center" in result

    def test_empty_alignments_list_leaves_html_unchanged(self):
        html = "<p>Hello</p>"
        assert add_alignment_to_html(html, []) == html

    def test_no_paragraphs_leaves_html_unchanged(self):
        html = "<div>No paragraphs</div>"
        assert add_alignment_to_html(html, ["center"]) == html


# ---------------------------------------------------------------------------
# get_footnote_from_html
# ---------------------------------------------------------------------------


class TestGetFootnoteFromHtml:
    # --- Return-value structure ---

    def test_returns_content_key(self):
        assert "content" in get_footnote_from_html(SINGLE_FN_HTML)

    def test_returns_footnotes_key(self):
        assert "footnotes" in get_footnote_from_html(SINGLE_FN_HTML)

    def test_footnotes_is_a_list(self):
        assert isinstance(get_footnote_from_html(SINGLE_FN_HTML)["footnotes"], list)

    # --- Single footnote ---

    def test_single_footnote_count(self):
        assert len(get_footnote_from_html(SINGLE_FN_HTML)["footnotes"]) == 1

    def test_footnote_id(self):
        fn = get_footnote_from_html(SINGLE_FN_HTML)["footnotes"][0]
        assert fn["id"] == "1"

    def test_footnote_tag(self):
        fn = get_footnote_from_html(SINGLE_FN_HTML)["footnotes"][0]
        assert fn["tag"] == "footnote-1"

    def test_footnote_backref(self):
        fn = get_footnote_from_html(SINGLE_FN_HTML)["footnotes"][0]
        assert fn["backref"] == "#footnote-ref-1"

    def test_footnote_text_contains_body_text(self):
        fn = get_footnote_from_html(SINGLE_FN_HTML)["footnotes"][0]
        assert "First footnote" in fn["text"]

    def test_footnote_text_excludes_backref_anchor(self):
        fn = get_footnote_from_html(SINGLE_FN_HTML)["footnotes"][0]
        assert "#footnote-ref-1" not in fn["text"]

    # --- Multiple footnotes ---

    def test_multi_footnote_count(self):
        assert len(get_footnote_from_html(MULTI_FN_HTML)["footnotes"]) == 2

    def test_multi_footnote_ids(self):
        ids = [fn["id"] for fn in get_footnote_from_html(MULTI_FN_HTML)["footnotes"]]
        assert "1" in ids and "2" in ids

    def test_multi_footnote_tags(self):
        tags = [fn["tag"] for fn in get_footnote_from_html(MULTI_FN_HTML)["footnotes"]]
        assert "footnote-1" in tags and "footnote-2" in tags

    # --- No footnotes ---

    def test_no_footnotes_returns_empty_list(self):
        assert get_footnote_from_html(NO_FN_HTML)["footnotes"] == []

    def test_no_footnotes_content_unchanged(self):
        assert get_footnote_from_html(NO_FN_HTML)["content"].strip() == NO_FN_HTML

    # --- Content integrity ---

    def test_footnote_ol_stripped_from_content(self):
        content = get_footnote_from_html(SINGLE_FN_HTML)["content"]
        assert '<li id="footnote-1">' not in content

    def test_main_paragraph_preserved_in_content(self):
        content = get_footnote_from_html(SINGLE_FN_HTML)["content"]
        assert "Main content." in content


# ---------------------------------------------------------------------------
# docx_preview_view – integration tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_render(monkeypatch):
    mock = MagicMock(return_value=MagicMock(status_code=200))

    monkeypatch.setattr("django_docx_footnote.admin.views.render", mock)
    return mock


@pytest.fixture()
def mock_http_response(monkeypatch):
    mock = MagicMock(return_value=MagicMock(status_code=400))

    monkeypatch.setattr("django_docx_footnote.admin.views.HttpResponse", mock)
    return mock


@pytest.fixture()
def mock_convert(monkeypatch):
    result = MagicMock()
    result.value = "<p>Hello world</p>"
    mock = MagicMock(return_value=result)

    monkeypatch.setattr("django_docx_footnote.admin.views.convert_to_html", mock)
    return mock


@pytest.mark.django_db
class TestDocxPreviewView:
    @pytest.fixture(autouse=True)
    def setUp(self):
        # Every test needs access to the request factory.
        self.rf = RequestFactory()
        self.staff_user = User.objects.create_user(
            username="staff", password="pass", is_staff=True
        )

    def _valid_request(self):
        uploaded_file = SimpleUploadedFile(
            "test.docx",
            build_docx(["center"]).getvalue(),  # bytes content
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        print(f"uploaded_file: {type(uploaded_file)}")
        req = self.rf.post(DOCX_PREVIEW_URL, {"file": uploaded_file})
        print(f"req.FILES: {list(req.FILES.keys())}")
        req.user = self.staff_user
        return req

    def _no_file_request(self):
        req = self.rf.post(DOCX_PREVIEW_URL)
        req.user = self.staff_user
        return req

    # --- authentication gate ------------------------------------------------

    def test_anonymous_user_is_redirected(self):
        from django.contrib.auth.models import AnonymousUser

        req = self.rf.post(DOCX_PREVIEW_URL)
        req.user = AnonymousUser()
        response = docx_preview_view(req)
        # staff_member_required returns a redirect (302), not a rendered page
        assert response.status_code == 302

    def test_anonymous_user_does_not_reach_render(self, mock_render):
        req = self.rf.post(DOCX_PREVIEW_URL)
        req.user = AnonymousUser()
        docx_preview_view(req)
        mock_render.assert_not_called()

    def test_non_staff_user_is_redirected(self, rf):
        regular = User.objects.create_user(
            username="regular", password="pass", is_staff=False
        )
        req = self.rf.post(DOCX_PREVIEW_URL)
        req.user = regular
        response = docx_preview_view(req)
        assert response.status_code == 302

    def test_render_called_on_valid_post(self, mock_render):
        docx_preview_view(self._valid_request())
        assert mock_render.called

    def test_on_valid_post_returns_200(self, mock_render):
        response = docx_preview_view(self._valid_request())
        assert response.status_code == 200

    def test_correct_template_name(self, mock_render):
        docx_preview_view(self._valid_request())
        _, template, _ = mock_render.call_args[0]
        assert template == "footnotes.html"

    def test_context_has_content_key(self, mock_render):
        docx_preview_view(self._valid_request())
        _, _, ctx = mock_render.call_args[0]
        assert "content" in ctx

    def test_context_has_footnotes_key(self, mock_render):
        docx_preview_view(self._valid_request())
        _, _, ctx = mock_render.call_args[0]
        assert "footnotes" in ctx

    def test_context_footnotes_is_list(self, mock_render):
        docx_preview_view(self._valid_request())
        _, _, ctx = mock_render.call_args[0]
        assert isinstance(ctx["footnotes"], list)

    def test_mammoth_called_once(self, mock_convert):
        docx_preview_view(self._valid_request())
        mock_convert.assert_called_once()

    def test_missing_file_returns_400(self, mock_http_response):
        docx_preview_view(self._no_file_request())
        mock_http_response.assert_called_once_with("Invalid request", status=400)

    def test_missing_file_does_not_call_render(self, mock_render):
        docx_preview_view(self._no_file_request())
        mock_render.assert_not_called()

    def test_footnotes_parsed_from_mammoth_output(self, mock_render):
        html_with_fn = (
            '<p>Text<sup id="footnote-ref-1"><a href="#footnote-1">1</a></sup></p>'
            "<ol>"
            '<li id="footnote-1"><p>A footnote.<a href="#footnote-ref-1">back</a></p></li>'
            "</ol>"
        )
        result = MagicMock()
        result.value = html_with_fn
        with patch(
            "django_docx_footnote.admin.views.convert_to_html", return_value=result
        ):
            docx_preview_view(self._valid_request())
        _, _, ctx = mock_render.call_args[0]
        assert len(ctx["footnotes"]) == 1
        assert ctx["footnotes"][0]["id"] == "1"
