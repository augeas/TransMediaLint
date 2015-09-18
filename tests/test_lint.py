from ..lint import annotate

def test_linter_annotates_bad_words():
    text_sample = "Mary is a tranny"

    results = annotate(text_sample)

    assert len(results) == 1

    annotation = results[0]
    assert annotation.what == "tranny"
    assert annotation.why == "Offensive"
    assert annotation.where == 10

