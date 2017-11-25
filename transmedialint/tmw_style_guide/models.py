
from django.db import models
from django.utils import timezone as localtimezone

from sources.models import Article, Source

class AnnotatedSource(models.Model):
    source = models.OneToOneField(Source, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(default=localtimezone.datetime.fromtimestamp(0.0))

annotation_type_choices = (('OFF','offensive'), ('INAC','inaccurate'), ('INAP','inappropriate'), ('INAPMED','inappropriate-medical'))

class Annotation(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.CharField(max_length=256)
    tag = models.CharField(max_length=5, choices = annotation_type_choices)
    label = models.CharField(max_length=64)
    position = models.IntegerField()
    
    class Meta:
        unique_together = (("article", "position"),)
        
    def __str__(self):
        return ': '.join([self.tag,' in '.join(['"'+self.text+'"', self.article.slug])])
