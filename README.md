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

![rated articles from The Sun](https://github.com/augeas/TransMediaLint/raw/master/img/rated_sun_articles.png)

What about the Daily Mail?

![rated articles from The Mail](https://github.com/augeas/TransMediaLint/raw/master/img/rated_mail_articles.png)
