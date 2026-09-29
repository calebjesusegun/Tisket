from app.repositories.search_repository import to_prefix_tsquery
from app.schemas.search import HighlightSegment as Seg
from app.services.search_service import (
    query_terms,
    segments_from_markers,
    segments_from_terms,
    snippet_around_first_match,
)


def test_query_terms_are_words_lowercased_and_unique() -> None:
    assert query_terms("Milk & bread, MILK!") == ["milk", "bread"]
    assert query_terms("   ") == []
    assert query_terms("a b c d e f g h i j") == ["a", "b", "c", "d", "e", "f", "g", "h"]


def test_prefix_tsquery_cannot_inject_operators() -> None:
    assert to_prefix_tsquery(query_terms("groc | !list:* & (x)")) == "groc:* & list:* & x:*"


def test_segments_from_markers() -> None:
    text = "Buy groceries and milk"
    assert segments_from_markers(text) == [
        Seg(text="Buy ", match=False),
        Seg(text="groceries", match=True),
        Seg(text=" and ", match=False),
        Seg(text="milk", match=True),
    ]
    assert segments_from_markers("plain") == [Seg(text="plain", match=False)]
    assert segments_from_markers("") == []


def test_segments_from_terms_case_insensitive_and_longest_first() -> None:
    assert segments_from_terms("Grocery groceries", ["groc", "groceries"]) == [
        Seg(text="Groc", match=True),
        Seg(text="ery ", match=False),
        Seg(text="groceries", match=True),
    ]


def test_segments_from_terms_edge_cases() -> None:
    assert segments_from_terms("", ["x"]) == []
    assert segments_from_terms("abc", []) == [Seg(text="abc", match=False)]
    assert segments_from_terms("a.b", ["."]) == [
        Seg(text="a", match=False),
        Seg(text=".", match=True),
        Seg(text="b", match=False),
    ]


def test_snippet_centres_on_first_match() -> None:
    text = ("word " * 50) + "needle " + ("word " * 50)
    snippet = snippet_around_first_match(text, ["needle"], radius=20)
    assert "needle" in snippet
    assert snippet.startswith("…")
    assert snippet.endswith("…")
    assert len(snippet) < 70


def test_snippet_without_match_uses_start() -> None:
    assert snippet_around_first_match("short text", ["zzz"]) == "short text"
    long = "x" * 500
    assert snippet_around_first_match(long, ["zzz"], radius=10) == "x" * 20 + "…"


def test_snippet_near_start_has_no_leading_ellipsis() -> None:
    assert snippet_around_first_match("needle in text", ["needle"]) == "needle in text"
