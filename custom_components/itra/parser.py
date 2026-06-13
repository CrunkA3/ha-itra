"""
Pure HTML parser for the ITRA RunnerSpace page.

This module has NO Home Assistant dependencies so it can be tested in
isolation without an HA environment.
"""
from __future__ import annotations

import logging
from typing import Any

from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

# CSS selectors — kept in sync with const.py values
_SELECTOR_LEVEL_COUNT = "span.level-count"
_SELECTOR_LEVEL = "span.level"


def parse_itra_html(html: str) -> dict[str, Any]:
    """
    Parse the ITRA RunnerSpace HTML and extract level_count and level.

    Returns a dict with keys:
      - level_count (int | None) — ITRA index
      - level (str)             — performance level string, "unknown" on failure
      - raw_html_snippet (str)  — up to 500 chars of matched tag HTML
    """
    soup = BeautifulSoup(html, "html.parser")

    # --- level_count ---
    level_count_tag = soup.select_one(_SELECTOR_LEVEL_COUNT)
    level_count: int | None = None
    if level_count_tag is None:
        _LOGGER.warning(
            "Could not find <span class='level-count'> in ITRA page. "
            "The page layout may have changed."
        )
    else:
        raw_value = level_count_tag.get_text(strip=True)
        try:
            level_count = int(raw_value)
        except ValueError:
            _LOGGER.warning(
                "Unexpected value for level-count: %r — expected an integer.",
                raw_value,
            )

    # --- level ---
    level_tag = soup.select_one(_SELECTOR_LEVEL)
    level: str = "unknown"
    if level_tag is None:
        _LOGGER.warning(
            "Could not find <span class='level'> in ITRA page. "
            "The page layout may have changed."
        )
    else:
        level = level_tag.get_text(strip=True) or "unknown"

    # Build a small HTML snippet for extra attributes
    raw_html_snippet = ""
    for tag in (level_count_tag, level_tag):
        if tag is not None:
            raw_html_snippet += str(tag)[:250]

    return {
        "level_count": level_count,
        "level": level,
        "raw_html_snippet": raw_html_snippet[:500],
    }
