"""Unit tests for the ITRA coordinator HTML parser."""

# ---------------------------------------------------------------------------
# We test _parse_html as a pure function without any HA machinery.
# BeautifulSoup is the only external dependency needed here.
# ---------------------------------------------------------------------------

SAMPLE_HTML_FULL = """
<!DOCTYPE html>
<html>
<body>
  <div class="runner-profile">
    <span class="level-count">388</span>
    <span class="level">Intermediate 4</span>
  </div>
</body>
</html>
"""

SAMPLE_HTML_MISSING_LEVEL_COUNT = """
<!DOCTYPE html>
<html>
<body>
  <div class="runner-profile">
    <span class="level">Elite 1</span>
  </div>
</body>
</html>
"""

SAMPLE_HTML_MISSING_LEVEL = """
<!DOCTYPE html>
<html>
<body>
  <div class="runner-profile">
    <span class="level-count">100</span>
  </div>
</body>
</html>
"""

SAMPLE_HTML_EMPTY = """
<!DOCTYPE html>
<html><body></body></html>
"""

SAMPLE_HTML_INVALID_LEVEL_COUNT = """
<!DOCTYPE html>
<html>
<body>
  <span class="level-count">not-a-number</span>
  <span class="level">Beginner 2</span>
</body>
</html>
"""

SAMPLE_HTML_WHITESPACE = """
<!DOCTYPE html>
<html>
<body>
  <span class="level-count">  42  </span>
  <span class="level">  Advanced 3  </span>
</body>
</html>
"""


def _parse(html: str) -> dict:
    """Load the pure parser module directly (bypasses HA-dependent __init__.py)."""
    import importlib.util
    import os

    parser_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "custom_components",
        "itra",
        "parser.py",
    )
    spec = importlib.util.spec_from_file_location("itra_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_itra_html(html)


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


def test_parse_full_sample():
    """Both elements are present and correctly parsed."""
    result = _parse(SAMPLE_HTML_FULL)
    assert result["level_count"] == 388
    assert result["level"] == "Intermediate 4"
    assert "raw_html_snippet" in result
    assert len(result["raw_html_snippet"]) > 0


def test_parse_whitespace_trimmed():
    """Whitespace around values must be stripped."""
    result = _parse(SAMPLE_HTML_WHITESPACE)
    assert result["level_count"] == 42
    assert result["level"] == "Advanced 3"


# ---------------------------------------------------------------------------
# Fallback / degraded-page tests
# ---------------------------------------------------------------------------


def test_parse_missing_level_count():
    """When level-count span is absent, level_count must be None."""
    result = _parse(SAMPLE_HTML_MISSING_LEVEL_COUNT)
    assert result["level_count"] is None
    assert result["level"] == "Elite 1"


def test_parse_missing_level():
    """When level span is absent, level must be 'unknown'."""
    result = _parse(SAMPLE_HTML_MISSING_LEVEL)
    assert result["level_count"] == 100
    assert result["level"] == "unknown"


def test_parse_empty_page():
    """Completely empty page: both fallbacks apply."""
    result = _parse(SAMPLE_HTML_EMPTY)
    assert result["level_count"] is None
    assert result["level"] == "unknown"


def test_parse_invalid_level_count_value():
    """Non-numeric level-count content falls back to None."""
    result = _parse(SAMPLE_HTML_INVALID_LEVEL_COUNT)
    assert result["level_count"] is None
    assert result["level"] == "Beginner 2"


# ---------------------------------------------------------------------------
# Snippet length test
# ---------------------------------------------------------------------------


def test_raw_html_snippet_max_length():
    """raw_html_snippet must not exceed 500 characters."""
    result = _parse(SAMPLE_HTML_FULL)
    assert len(result["raw_html_snippet"]) <= 500
