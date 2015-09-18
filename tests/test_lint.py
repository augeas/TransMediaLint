from ..lint import annotate

def test_linter_annotates_one_bad_word():
    text_sample = "Mary had a sex swap"

    results = annotate(text_sample)

    assert len(results) == 1

    annotation = results[0]
    assert annotation.what == "sex swap"
    assert annotation.why == "offensive"
    assert annotation.where == 11

def test_linter_annotates_multiple_bad_words():
    text_sample = "post op sex change"

    results = annotate(text_sample)

    assert len(results) == 2

    annotation = results[0]
    assert annotation.what == "post op"
    assert annotation.why == "offensive"
    assert annotation.where == 0

    annotation = results[1]
    assert annotation.what == "sex change"
    assert annotation.why == "offensive"
    assert annotation.where == 8
