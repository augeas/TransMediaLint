from rest_framework import serializers

from django.db.models import Count

from sources.models import Article
from .models import Annotation

class LintedArticleSerializer(serializers.ModelSerializer):
    annotation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        exclude = ('page',)
        
    def get_annotation_count(self, obj):
        annot_query = Annotation.objects.filter(article=obj).values('tag').annotate(count=Count('tag'))
        counts = {annot['tag']:annot['count'] for annot in annot_query}
        counts['total'] = sum(counts.values())
        return counts