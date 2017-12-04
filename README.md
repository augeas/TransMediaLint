# TransMediaLint

In 2015 I found myself at the [TransCode](http://trans-code.org/) [event](http://2015.pyconuk.org/transcode/) at
[PyCon UK](http://pyconuk.org). I was aware of [JobLint](http://joblint.org/), a tool for checking tech job
adverts for the worst excesses of [recruiters](https://i.pinimg.com/originals/8c/58/4c/8c584c601031ce0f863cb0f8b8e71887.jpg)
and [start-up culture](https://pbs.twimg.com/media/CfNJTAHWAAAik5I.png). I wondered if the
[Trans Media Watch](http://www.transmediawatch.org/)
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf) could be automated.
In the end, most of it could be applied with simple
[regular expressions](https://pbs.twimg.com/media/Cr7mS_OWcAA7Hzt.jpg), and I thought little of it for a
couple of years.

Given the state of the world, I've decided to revive it, this time as a web-app based on the
Django Rest Framework, Postgres, Solr and Pandas/Bokeh. So far,it seems work on PyPy reasonably well.
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
than speaking for it.

What about the Daily Mail?

![rated articles from The Mail](https://github.com/augeas/TransMediaLint/raw/master/img/rated_mail_articles.png)

```http://localhost:8000/worstlintedarticles/```

![worst article so far](https://github.com/augeas/TransMediaLint/raw/master/img/worst_mail.png)

```http://localhost:8000/annotations/?article__id=717```

![worst article annotations](https://github.com/augeas/TransMediaLint/blob/master/img/worst_mail_annots.png)