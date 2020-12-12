

from rest_framework import serializers

from tml_corpus.models import NamedEntity


class NamedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NamedEntity
        fields = ('text', 'label')


