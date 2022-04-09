
# TransMediaLint

This software will *probably* not tell you anything you don't already know.

It *might* help quantify things you already knew.

The [style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf)
produced by [Trans Media Watch](http://www.transmediawatch.org/), like the
[Media Reference Guide](https://www.glaad.org/reference/transgender) released
by [GLAAD](https://www.glaad.org/) and the
[Guide For Journalists](https://tgeu.org/wp-content/uploads/2016/07/TGEU_journalistGuide16LR_singlepages.pdf)
released by the [TGEU](https://tgeu.org/) are designed to help Journalists
avoid transphobic language, rather than measure it. However, most of the rules
from these guides can be implemented with simple regular expressions. This
software crawls (UK) media sites, applies the rules to articles, and examines
how the usage of transphobic terms and who and what they are applied to has
changed. It was first thought of at the 2015 [TransCode](http://trans-code.org/)
[event](http://2015.pyconuk.org/transcode/) held at [PyCon UK](http://pyconuk.org).

* There is a *noticable variation* in the *frequency* of transphobic terms across UK
media websites.
* There is a *noticable variation* in the *kinds* of transphobic terms across media
websites.
* There is a *noticable variation* in the people and organisations mentioned in
articles, depending on whether potentially transphobic terms are used.

### Some Caveats

* This software was not solicited by the three organizations mentioned.
* The style-guides take pains to mention that some terms sometimes considered
transphobic may be used by trans people about themselves.
* Some terms may be used in direct quotations, or to discuss transphobia rather
than engage in it.
* The presence or absence of a term is not an absolute indication of transphobia
or otherwise.
* Website search features are not exaustive, so the frequency of articles may be
less reliale further back into the past.
* You are *STRONGLY DISCOURAGED* from deploying this software in its current
state on a public-facing webserver.
* The warranty of this software according to its License is
[NONE AT ALL](http://www.apache.org/licenses/LICENSE-2.0.txt).

All this software does is to *Count Things*. Interpretation should be left to
the reader.

## Article Frequency

By default, articles containing the terms `transgender`, `transexual` and
`intersex` are searched for. Articles are not counted if they do not contain
one of the terms, regardless of their appearance in search results. They are
rated `red` if potentially offsensive, inaccurate or inappropriate terms are
used, `yellow` if outdated or inappropriate medical terms are used, or `green`
if no annotations are found.

![rated articles from The Sun](https://github.com/augeas/TransMediaLint/raw/master/img/rated_sun_articles_3_22.png)
![rated articles from The Daily Mail](https://github.com/augeas/TransMediaLint/raw/master/img/rated_daily_mail_articles_3_22.png)

Articles from magazines like "The Spectator", and online analogues such as
"Spiked" or "The Critic" exhibit somewhat more frequent annotations from the
style-guides:

![rated articles from The Spectator](https://github.com/augeas/TransMediaLint/raw/master/img/rated_spectator_articles.png)
![rated articles from Spiked](https://github.com/augeas/TransMediaLint/raw/master/img/rated_spiked_articles.png)
![rated articles from The Critic](https://github.com/augeas/TransMediaLint/raw/master/img/rated_critic_articles_3_22.png)

Although The Guardian receives fewer annotations, it should be noted that this approach
will not detect incidents such as its
[selective editing](https://www.pinknews.co.uk/2021/09/08/judith-butler-guardian-interview-terf-trans/)
of an interview with [Judith Butler](https://en.wikipedia.org/wiki/Judith_Butler), or its
[focus during its interview](https://www.pinknews.co.uk/2022/02/19/margaret-atwood-hadley-freeman-trans-gender-critical/) with "Handmaid's Tale" author [Margaret Atwood](http://margaretatwood.ca/).

![rated articles from The Guardian](https://github.com/augeas/TransMediaLint/raw/master/img/rated_guardian_articles_3_22.png)

It is not the intention of this software to circumvent pay-walls. Analysis of
"The Times" and "Telegraph" is being explored through the use of
[Splash](https://github.com/scrapinghub/splash) to crawl the sites with
legitimate credentials.

## Annotation Lable Frequency

It is a simple matter to plot the monthly count of each type of annotation.
The keys on the right of the charts list terms in order of decreasing frequency.
Tabloids like "The Sun" and "The Daily Mail" have broadly similar results.
The most common annotation "sex-change", is often considered
[sensationalism](https://www.glaad.org/reference/transgender).
"The Daily Mail" site features large numbers of syndicated articles from the
US, which may explain the prominence of the term "bathroom bill".
The simple approach of counting annotations cannot take into account the
prominence given to articles, or their appearance on the
[front-page](https://twitter.com/mimmymum/status/1511998806614851584), however.

![annotation labels from The Sun](https://github.com/augeas/TransMediaLint/raw/master/img/the_sun_annotation_labels.png)
![annotation labels from Daily Mail](https://github.com/augeas/TransMediaLint/raw/master/img/the_daily_mail_annotation_labels.png)

Magazines such as "The Spectator" and online equivalents have a substantially
different focus. In all cases, the term "transgenderism", widely considered
[perjorative](https://www.glaad.org/reference/trans-terms), is the most frequent.

![annotation labels from The Spectator](https://github.com/augeas/TransMediaLint/raw/master/img/the_spectator_annotation_labels.png)
![annotation labels from Spiked](https://github.com/augeas/TransMediaLint/raw/master/img/spiked_annotation_labels.png)
![annotation labels from The Critic](https://github.com/augeas/TransMediaLint/raw/master/img/the_critic_annotation_labels.png)

"Transgenderism" is also more common than "sex-change" in The Guardian, though
by far the most common term is "passing", which of course has a frequent common
usage as well as its more controversial one.

![annotation labels from The Guardian](https://github.com/augeas/TransMediaLint/raw/master/img/the_guardian_annotation_labels.png)

## Named Entity Recognition

The Python NLP library [SpaCy](https://spacy.io/) can perform
[named entity recognition](https://spacy.io/usage/linguistic-features#named-entities)
(NER) to extract people, places, organisations, etc... from texts. The most commonly
occuring entities in articles can be plotted according to the article ratings.

For "The Spectator", in articles rated green, the most common entities are
political parties, countries,
[All-Party Parliamentary Groups](https://www.parliament.uk/about/mps-and-lords/members/apg/)
(APPG) and Jordan Peterson. The red-rated entities start with 
[the Harry Miller case](https://www.pinknews.co.uk/2021/12/20/harry-miller-court-appeals-gender-critical-hate/).


![named entities from Spectator articles rated green](https://github.com/augeas/TransMediaLint/raw/master/img/the_spectator_green_entities.png)
![named entities from Spectator articles rated red](https://github.com/augeas/TransMediaLint/raw/master/img/the_spectator_red_entities.png)


