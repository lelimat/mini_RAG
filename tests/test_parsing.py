from app.ingest import parse_verse_line


def test_parse_numeric_prefix_book() -> None:
    verse = parse_verse_line("1 Corinthians 13:4 Charity suffereth long, and is kind; charity envieth not;")

    assert verse.metadata.book == "1 Corinthians"
    assert verse.metadata.chapter == 13
    assert verse.metadata.verse == 4
    assert verse.metadata.testament == "New"
    assert verse.metadata.reference == "1 Corinthians 13:4"


def test_parse_song_of_solomon() -> None:
    verse = parse_verse_line("Song of Solomon 2:1 I am the rose of Sharon, and the lily of the valleys.")

    assert verse.metadata.book == "Song of Solomon"
    assert verse.metadata.chapter == 2
    assert verse.metadata.verse == 1
    assert verse.metadata.testament == "Old"
