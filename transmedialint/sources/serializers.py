
from rest_framework import serializers

from sources.models import Article, Author, Source


class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('name', 'slug')

        
class SourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Source
        fields = ('title', 'slug')

        
class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True, many=False)
    
    class Meta:
        model = Article
        fields = ('title', 'slug', 'source', 'url', 'author', 'date_published')
        
        
class CrawlerSerializer(serializers.Serializer):
    title = serializers.CharField()
    crawler = serializers.CharField()                         

