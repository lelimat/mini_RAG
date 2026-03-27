from app.retrieve import build_retrieval_filter


def test_build_testament_only_filter() -> None:
    assert build_retrieval_filter(testament="Old") == {"testament": "Old"}


def test_build_combined_filter_with_books() -> None:
    where = build_retrieval_filter(testament="New", books=["John", "Romans"])

    assert where == {
        "$and": [
            {"testament": "New"},
            {"book": {"$in": ["John", "Romans"]}},
        ]
    }


def test_build_book_only_filter() -> None:
    assert build_retrieval_filter(testament="Both", books=["Genesis"]) == {"book": "Genesis"}
