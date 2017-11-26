from rest_framework import serializers

from django.db.models import Count

from sources.models import Article, Author
from sources.serializers import AuthorSerializer, SourceSerializer

from .models import Annotation

class LintedArticleSerializer(serializers.ModelSerializer):
    annotation_count = serializers.SerializerMethodField()
    author = AuthorSerializer(read_only=True, many=True)
    source = SourceSerializer(read_only=True, many=False)
    
    class Meta:
        model = Article
        exclude = ('id', 'page', 'broken')
        
    def get_annotation_count(self, obj):
        annot_query = Annotation.objects.filter(article=obj).values('tag').annotate(count=Count('tag'))
        counts = {annot['tag']:annot['count'] for annot in annot_query}
        counts['total'] = sum(counts.values())
        return counts
    
class CountedAnnotSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    
    class Meta:
        model = Annotation
        fields = ('count', 'label', 'tag')

class RatedAuthorSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    articles = serializers.IntegerField()
    
    class Meta:
        model = Author
        fields = ('articles', 'count', 'name', 'slug')
