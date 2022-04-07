
from zipfile import ZipFile

from bs4 import BeautifulSoup

from django.db import models
from django.utils import timezone as localtimezone
from django.utils.text import slugify


class Source(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32)
    last_scraped = models.DateTimeField(default=localtimezone.datetime.fromtimestamp(0.0))
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True)
    

def article_directory_path(instance, filename):
    return '/'.join(['article_dump', instance.source.name, str(instance.date_published.year), str(instance.date_published.month), filename])


def preview_directory_path(instance, filename):
    return '/'.join(['article_dump', instance.source.name, 'previews', str(instance.date_published.year), str(instance.date_published.month), filename])


class Article(models.Model):
    title = models.CharField(max_length=256)
    author = models.ManyToManyField(Author)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    url = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=256)
    date_published = models.DateTimeField(default=localtimezone.datetime.fromtimestamp(0.0))
    date_retrieved = models.DateTimeField(default=localtimezone.datetime.fromtimestamp(0.0))    
    page = models.FileField(upload_to=article_directory_path)
    preview = models.FileField(upload_to=preview_directory_path, null=True)
    broken = models.BooleanField(default=False)


    def read_zip(self):
        zip_path = self.page.path

        with ZipFile(zip_path) as zip:
            fname = zip.infolist()[0].filename
            with zip.open(fname) as fl:
                return fl.read().decode('utf-8')


    def clean_strings(self):
        soup = BeautifulSoup(self.read_zip(), 'html5lib')
        for tag in soup(['script','img','style']):
            tag.extract()
        yield from soup.stripped_strings


        
    def text(self):
        return '\n'.join(self.clean_strings())


    def as_item(self):
        try:
            preview = self.preview.read().decode('utf-8')
        except:
            preview = None
        
        return {
            'content': self.read_zip(),
            'title': self.title,
            'date_published': self.date_published.isoformat(),
            'url': self.url,
            'byline': ' & '.join(auth.name for auth in self.author.get_queryset()),
            'preview': preview,
            'article_id': self.id,
            'source_id': self.source.id
        }



    def __str__(self):
        return self.slug

    
    class Meta:
        ordering = ('-date_published',)
        
