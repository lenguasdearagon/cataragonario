from linguatec_lexicon.models import Entry
from rest_framework import serializers


class EntryNearSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='word', read_only=True)
    term = serializers.CharField(source='translation')
    url = serializers.HyperlinkedRelatedField(source='word', view_name='word-detail', read_only=True)
    _word = serializers.SlugRelatedField(source='word', slug_field='term', read_only=True)

    class Meta:
        model = Entry
        fields = ('url', 'id', 'term', '_word')
