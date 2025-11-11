# tests/test_common.py


import src.ui.common as common


def test_load_css_reads_and_marksdown(monkeypatch, tmp_path):
    # tehdään feikkicss
    css_file = tmp_path / "test.css"
    css_file.write_text("body { background: red; }", encoding="utf-8")

    # ohitetaan asset_path palauttamaan tämä
    monkeypatch.setattr(common, "asset_path", lambda name: css_file)

    called = {}

    def fake_markdown(html, unsafe_allow_html=False):
        called["html"] = html
        called["unsafe"] = unsafe_allow_html

    monkeypatch.setattr(common.st, "markdown", fake_markdown)

    common.load_css("test.css")

    assert "background: red" in called["html"]
    assert called["unsafe"] is True


def test_load_css_missing_file_does_nothing(monkeypatch, tmp_path):
    missing = tmp_path / "not-there.css"
    monkeypatch.setattr(common, "asset_path", lambda name: missing)

    called = {"markdown": False}

    def fake_markdown(*a, **k):
        called["markdown"] = True

    monkeypatch.setattr(common.st, "markdown", fake_markdown)

    common.load_css("not-there.css")
    assert called["markdown"] is False


def test_section_title_renders_html(monkeypatch):
    called = {}

    def fake_markdown(html, unsafe_allow_html=False):
        called["html"] = html
        called["unsafe"] = unsafe_allow_html

    monkeypatch.setattr(common.st, "markdown", fake_markdown)

    common.section_title("Hello", mt=5, mb=3)
    assert "Hello" in called["html"]
    assert "margin:5px 0 3px 0" in called["html"]
    assert called["unsafe"] is True


def test_card_renders_structure(monkeypatch):
    called = {}

    def fake_markdown(html, unsafe_allow_html=False):
        called["html"] = html
        called["unsafe"] = unsafe_allow_html

    monkeypatch.setattr(common.st, "markdown", fake_markdown)

    common.card("Title", "<p>Body</p>", height_dvh=20)

    html = called["html"]
    assert '<section class="card"' in html
    assert "Title" in html
    assert "<p>Body</p>" in html
    assert "min-height:20dvh" in html
    assert called["unsafe"] is True
