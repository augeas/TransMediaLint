
from django.db import models

from sources.models import Article


class NamedEntity(models.Model):
    text = models.CharField(max_length=128)
    label = models.CharField(max_length=32)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['text', 'label'], name='unique entities')]

    
class ArticleEntity(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    entity = models.ForeignKey(NamedEntity, on_delete=models.CASCADE)
    position = models.IntegerField()

