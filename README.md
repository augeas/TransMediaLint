# TransMediaLint

In 2015 I found myself at the [TransCode](http://trans-code.org/) [event](http://2015.pyconuk.org/transcode/) at
[PyCon UK](http://pyconuk.org). I was aware of [JobLint](http://joblint.org/), a tool for checking tech job
adverts for the worst excesses of [recruiters](https://i.pinimg.com/originals/8c/58/4c/8c584c601031ce0f863cb0f8b8e71887.jpg)
and [start-up culture](https://pbs.twimg.com/media/CfNJTAHWAAAik5I.png). I wondered if the
[Trans Media Watch](http://www.transmediawatch.org/)
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf) could be automated.
In the end, most of it could be applied with simple
[regular expressions](https://pbs.twimg.com/media/Cr7mS_OWcAA7Hzt.jpg), and I thought little of the project for a
couple of years.

Given the state of the world, I've decided to revive it, this time as a web-app based on the
Django Rest Framework, Postgres, Solr and Pandas/Bokeh. So far, it seems work on PyPy reasonably well.
The idea is that it crawls and annotates media websites automatically, and the user can explore and
search the results. Let us consider The Sun newspaper's website: 

```http://localhost:8000/charts/rated_articles?source=the-sun```

The web-crawler searches the Sun's website for articles containing the terms "transgender" or "transsexual",
which are then annotated by a set of
[regexes](https://github.com/augeas/TransMediaLint/blob/master/transmedialint/tmw_style_guide/rules.py).
They are aggregated by month of publication, their frequencies are plotted using Bokeh:

![rated articles from The Sun](https://github.com/augeas/TransMediaLint/raw/master/img/rated_sun_articles.png)

It seems to be getting busier.
Articles with no annotations are plotted in green, but of course this doesn't mean that none of them are
problematic. Those with potentially inappropriate commonly used medical or legal terms are plotted in
yellow, inaccurate, inappropriate or downright offensive terms are plotted in red. Hopefully, this is a
fair representation of the
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf), that amplifies it rather
than speaking for it. One of the things to do reasonably shortly would be to try
[topic-modelling](https://radimrehurek.com/gensim/). Will the topics of poorly-rated
articles be more puerile and tawdry? How will topics differ between sources?

What about the Daily Mail?

```http://localhost:8000/charts/rated_articles?source=the-daily-mail```

![rated articles from The Mail](https://github.com/augeas/TransMediaLint/raw/master/img/rated_mail_articles.png)

It's *obsessed*, and getting more so. The absolute numbers of bad articles remain
roughly constant, even though they're getting proportionally fewer. We can use the
REST API to discover that the
[very worst article](http://www.dailymail.co.uk/news/article-2921528/The-man-s-TWO-sex-changes-Incredible-story-Walt-Laura-REVERSED-operation-believes-surgeons-quick-operate.html)
in terms of the number of annotations is from the Mail:

```http://localhost:8000/worstlintedarticles/```

![worst article so far](https://github.com/augeas/TransMediaLint/raw/master/img/worst_mail.png)

We can also find its annotations:

```http://localhost:8000/annotations/?article__id=717```

![worst article annotations](https://github.com/augeas/TransMediaLint/blob/master/img/worst_mail_annots.png)

(Note that the term "transgenderism" isn't in the original
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf), but
I've added it. I'll leave it to others to
[explain why it shouldn't be used](https://www.quora.com/Is-transgenderism-the-correct-word-to-use-in-regards-to-trans-people).)

## Getting Started

If you want to play along with the story so far, first get [docker-compose](https://docs.docker.com/compose/), and clone the repo. The containers can be pulled and built with
the script the initializes the database. It'll take a while:

```git clone https://github.com/augeas/TransMediaLint.git
cd TransMediaLint
sudo ./init_db
```

Next grab some articles and annotate them in the Django console:


```sudo ./shell
from sources.crawlers import TheSun, TheDailyMail
TheSun.scrape(['transgender','transsexual'])
from tmw_style_guide.annotate import get_annotations
get_annotations(TheSun)
```

The Daily Mail will take *ages*. Quit the shell with "Ctrl-D", then start the server with:

```sudo docker-compose up```

## To Do:

Before anyone else moderately technical wastes time on this it needs:

- [X] the Django app to be properly Dockerised
- [ ] automated scraping and annotating via Celery
- [ ] cacheing with Redis

Before it's fit for *civilians* it needs:

- [ ] a (probably) AngularJS front-end to consume the API
- [ ] loads more web-crawlers for more sources
- [ ] a search API to put Solr to good use
- [ ] shoving into a VirtualBox appliance for the hard-of-Docker.
- [ ] .csv downloads