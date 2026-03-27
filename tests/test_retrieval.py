from app.retrieve import format_query_results


def test_format_query_results_shape() -> None:
    results = {
        "documents": [["In the beginning God created the heaven and the earth."]],
        "metadatas": [[{
            "reference": "Genesis 1:1",
            "book": "Genesis",
            "chapter": 1,
            "verse": 1,
            "testament": "Old",
        }]],
        "distances": [[0.25]],
    }

    passages = format_query_results(results)

    assert len(passages) == 1
    assert passages[0].reference == "Genesis 1:1"
    assert passages[0].book == "Genesis"
    assert passages[0].text.startswith("In the beginning")
    assert passages[0].distance == 0.25
    assert passages[0].score is not None
