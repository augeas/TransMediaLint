from ..lint import annotate, score

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

def test_scoring():
    text_sample = """

    This is some test text that contains some words that should trigger the linter
    and produce a negative score

    For example, it has the word post op which can be offensive. This scores -5

    (-5)

    It also has this: sex change - another -5

    (-10)

    In addition, it refers to gender identity disorder which is an inappropriate thing to refer
    to, scoring -1

    (-11)

    """

    assert score(text_sample) == -11


