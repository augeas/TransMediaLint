from rest_framework import serializers

from dateutil import parser
from django.db.models import Count

from sources.models import Article, Author, Source
from sources.serializers import AuthorSerializer, SourceSerializer,  ArticleSerializer

from .models import Annotation, RatedArticle


class RatedArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RatedArticle
        fields = ('article', 'offensive', 'inaccurate', 'inappropriate')
        
        depth = 2


class RatedArticleExportSerializer(serializers.ModelSerializer):
    article = ArticleSerializer()

    class Meta:
        model = RatedArticle
        fields = ('article', 'offensive', 'inaccurate', 'inappropriate')

        depth = 2

    def to_representation(self, obj):
        rep = super().to_representation(obj)
        article_rep = rep.pop('article')
        for key in ('title', 'slug', 'date_published', 'url'):
            rep[key] = article_rep[key]
        rep['author'] = article_rep['author'][0]['name']
        rep['source'] = article_rep['source']['slug']

        published = parser.parse(article_rep['date_published'])

        rep['path'] = '{}/content/{}/{}/{}_content'.format(
            article_rep['source']['name'],
            published.year, published.month,
            article_rep['slug']
        )

        return rep

class LintedArticleSerializer(serializers.ModelSerializer):
    annotation_count = serializers.SerializerMethodField()
    author = AuthorSerializer(read_only=True, many=True)
    source = SourceSerializer(read_only=True, many=False)
    
    class Meta:
        model = Article
        exclude = ('page', 'preview', 'broken')
        
    def get_annotation_count(self, obj):
        annot_query = Annotation.objects.filter(article=obj).values('tag').annotate(count=Count('tag'))
        counts = {annot['tag']:annot['count'] for annot in annot_query}
        counts['total'] = sum(counts.values())
        return counts

class AnnotSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = Annotation
            exclude = ('id', 'article')
    
class CountedAnnotSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    
    class Meta:
        model = Annotation
        fields = ('count', 'label', 'tag')

class RatedAuthorSerializer(serializers.ModelSerializer):
    annots = serializers.IntegerField()
    articles = serializers.IntegerField()
    article = ArticleSerializer(read_only=True, many=True)
    
    class Meta:
        model = Author
        fields = ('articles', 'annots', 'name', 'slug', 'article')    
