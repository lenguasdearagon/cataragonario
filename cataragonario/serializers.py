from linguatec_lexicon.models import Entry
from linguatec_lexicon.serializers import DiatopicVariationSerializer
from linguatec_lexicon.serializers import \
    EntrySerializer as LinguatecEntrySerializer
from linguatec_lexicon.serializers import \
    WordSerializer as LinguatecWordSerializer
from rest_framework import serializers


class EntryNearSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='word', read_only=True)
    term = serializers.CharField(source='translation')
    url = serializers.HyperlinkedRelatedField(source='word', view_name='word-detail', read_only=True)
    _word = serializers.SlugRelatedField(source='word', slug_field='term', read_only=True)

    class Meta:
        model = Entry
        fields = ('url', 'id', 'term', '_word')


class EntrySerializer(LinguatecEntrySerializer):
    variation = serializers.SerializerMethodField()

    class Meta(LinguatecEntrySerializer.Meta):
        pass

    def get_variation(self, obj):
        """
        Entries with the same translation are grouped on a single one with many variations
        instead of many "duplicated" entries with a single one
            normative language, then variation is None --> None
            if variation --> [variation1, variation2, variation3]
        """
        if not obj.variations:
            return None

        data = []
        for v in obj.variations:
            if v is None:
                continue
            srlz = DiatopicVariationSerializer(instance=v)
            data.append(srlz.data)

        return data


class WordSerializer(LinguatecWordSerializer):
    entries = serializers.SerializerMethodField()

    class Meta(LinguatecWordSerializer.Meta):
        pass

    def get_entries(self, obj):
        final_entries = []
        grouped_entries = {}
        for e in obj.entries.all():
            # we don't want to group variation__isnull
            if e.variation is None:
                e.variations = []
                final_entries.append(e)

            elif e.translation in grouped_entries:
                match_entry = grouped_entries[e.translation]
                match_entry.variations.append(e.variation)

            else:
                # initialized multiple variations of current entry
                # and store as base entry of grouped variations
                e.variations = [e.variation]
                grouped_entries[e.translation] = e

        final_entries += list(grouped_entries.values())

        data = []
        for e in final_entries:
            srlz = EntrySerializer(instance=e)
            data.append(srlz.data)

        return data
