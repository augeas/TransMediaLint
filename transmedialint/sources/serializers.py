from rest_framework import serializers

from sources.models import Author, Source

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('name', 'slug')
        
class SourceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Source
        fields = ('title', 'slug')