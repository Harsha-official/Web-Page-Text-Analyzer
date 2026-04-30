import pytest
from unittest.mock import patch, MagicMock
from project import scrape_text, get_word_frequency, compute_text_stats, save_report


# --- scrape_text ---

def test_scrape_text_bad_url_no_scheme():
    with pytest.raises(ValueError):
        scrape_text("example.com/page")

def test_scrape_text_bad_url_ftp():
    with pytest.raises(ValueError):
        scrape_text("ftp://example.com")

def test_scrape_text_empty_string():
    with pytest.raises(ValueError):
        scrape_text("")

@patch("project.requests.get")
def test_scrape_text_404(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = __import__("requests").exceptions.HTTPError(
        response=MagicMock(status_code=404)
    )
    mock_get.return_value = mock_resp
    with pytest.raises(ValueError, match="HTTP"):
        scrape_text("https://example.com/notfound")

@patch("project.requests.get")
def test_scrape_text_returns_page_text(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.text = "<html><body><p>Hello world, this is a test.</p></body></html>"
    mock_get.return_value = mock_resp

    result = scrape_text("https://example.com")
    assert "Hello world" in result

@patch("project.requests.get")
def test_scrape_text_removes_scripts_and_styles(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.text = (
        "<html><body>"
        "<script>var x = 1;</script>"
        "<style>.thing { color: red }</style>"
        "<p>Actual content.</p>"
        "</body></html>"
    )
    mock_get.return_value = mock_resp

    result = scrape_text("https://example.com")
    assert "Actual content" in result
    assert "var x" not in result
    assert "color" not in result


# --- get_word_frequency ---

def test_get_word_frequency_ordering():
    text = "apple banana apple cherry apple banana"
    result = get_word_frequency(text, top_n=3)
    words = [w for w, _ in result]
    assert words[0] == "apple"
    assert words[1] == "banana"

def test_get_word_frequency_stop_words():
    text = "the the the and and python python python"
    result = get_word_frequency(text, top_n=5)
    words = [w for w, _ in result]
    assert "the" not in words
    assert "and" not in words
    assert "python" in words

def test_get_word_frequency_counts():
    text = "cat cat cat dog dog bird"
    result = dict(get_word_frequency(text, top_n=5))
    assert result["cat"] == 3
    assert result["dog"] == 2
    assert result["bird"] == 1

def test_get_word_frequency_top_n():
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda"
    result = get_word_frequency(text, top_n=5)
    assert len(result) <= 5

def test_get_word_frequency_empty_input():
    assert get_word_frequency("") == []
    assert get_word_frequency("   ") == []

def test_get_word_frequency_short_words():
    text = "is it an at ok go to be do we us me he"
    result = get_word_frequency(text, top_n=10)
    for word, _ in result:
        assert len(word) >= 3


# --- compute_text_stats ---

def test_compute_text_stats_empty():
    stats = compute_text_stats("")
    assert stats["word_count"] == 0
    assert stats["sentence_count"] == 0
    assert stats["readability_level"] == "N/A"

def test_compute_text_stats_word_count():
    stats = compute_text_stats("Hello world this is four words.")
    assert stats["word_count"] == 6

def test_compute_text_stats_sentence_count():
    stats = compute_text_stats("Hello world. How are you? I am fine!")
    assert stats["sentence_count"] == 3

def test_compute_text_stats_avg_word_length():
    stats = compute_text_stats("Python programming is great.")
    assert stats["avg_word_length"] > 0

def test_compute_text_stats_readability_easy():
    stats = compute_text_stats("Go. Run. Jump. Stop. Wait. Look. See.")
    assert stats["readability_level"] == "Easy"

def test_compute_text_stats_readability_complex():
    long_text = " ".join(["word"] * 100) + "."
    stats = compute_text_stats(long_text)
    assert stats["readability_level"] == "Complex"

def test_compute_text_stats_all_keys():
    stats = compute_text_stats("Some text here.")
    for key in ["char_count", "word_count", "sentence_count", "avg_word_length", "avg_sentence_length", "readability_level"]:
        assert key in stats


# --- save_report ---

def test_save_report_creates_file(tmp_path):
    out = tmp_path / "report.txt"
    stats = compute_text_stats("Hello world. This is a test.")
    freq = get_word_frequency("Hello world test test test")
    save_report("Hello world. This is a test.", stats, freq, str(out))
    assert out.exists()

def test_save_report_has_stats_in_it(tmp_path):
    out = tmp_path / "report.txt"
    stats = compute_text_stats("Hello world.")
    freq = [("hello", 5), ("world", 3)]
    save_report("Hello world.", stats, freq, str(out))
    content = out.read_text(encoding="utf-8")
    assert "words" in content
    assert "readability" in content

def test_save_report_has_keywords(tmp_path):
    out = tmp_path / "report.txt"
    stats = compute_text_stats("Python is great.")
    freq = [("python", 10), ("great", 4)]
    save_report("Python is great.", stats, freq, str(out))
    content = out.read_text(encoding="utf-8")
    assert "python" in content
    assert "great" in content

def test_save_report_returns_abs_path(tmp_path):
    out = tmp_path / "out.txt"
    stats = compute_text_stats("Test.")
    result = save_report("Test.", stats, [], str(out))
    assert result == str(out.resolve())