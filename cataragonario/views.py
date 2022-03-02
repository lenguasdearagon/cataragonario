from django.contrib.postgres.search import TrigramSimilarity
from linguatec_lexicon.models import Entry, Word
from linguatec_lexicon.serializers import WordNearSerializer, WordSerializer
from linguatec_lexicon.views import DefaultLimitOffsetPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import EntryNearSerializer

MODE_DIALECTAL = 'dialectal'
MODE_REVERSE = 'reverse'
MODE_STANDAR = 'standar'

SEARCH_MODES = (MODE_STANDAR, MODE_REVERSE, MODE_DIALECTAL)

# TODO add method to WordManager
def search_near_dialectal(self, query, lex=None, mode=MODE_STANDAR):
    # https://docs.djangoproject.com/en/2.1/ref/contrib/postgres/search/#trigram-similarity
    # https://www.postgresql.org/docs/current/pgtrgm.html
    # 0 means totally different
    # 1 means identical
    MIN_SIMILARITY = 0.2

    qs = self._filter_by_lexicon(lex)

    if mode in [MODE_REVERSE, MODE_DIALECTAL]:
        if mode == MODE_REVERSE:
            qs = Entry.objects.filter(variation__isnull=True)
        elif mode == MODE_DIALECTAL:
            qs = Entry.objects.filter(variation__isnull=False)

        qs = qs.annotate(similarity=TrigramSimilarity('translation', query)).filter(
            similarity__gt=MIN_SIMILARITY).distinct('translation', 'similarity')

    else:
        qs = qs.annotate(
            similarity=TrigramSimilarity('term', query),
        ).filter(similarity__gt=MIN_SIMILARITY)

    return qs.order_by('-similarity')


# TODO add method to WordManager
# --> https://www.ianlewis.org/en/dynamically-adding-method-classes-or-class-instanc
def search_dialectal(self, query, lex=None, mode=MODE_STANDAR):
    MIN_SIMILARITY = 0.3
    iregex = r"\y{0}\y"

    # query = self._clean_search_query(query)
    # qs = self._filter_by_lexicon(lex)
    qs = self

    if mode == MODE_REVERSE:
        qs = qs.filter(entries__translation=query, entries__variation__isnull=True).distinct()

    elif mode == MODE_DIALECTAL:
        qs = qs.filter(entries__translation=query, entries__variation__isnull=False).distinct()

    else:   # STANDAR MODE
        qs = qs.filter(
            term__iregex=iregex.format(query)
        ).annotate(similarity=TrigramSimilarity('term', query)
                   ).filter(similarity__gt=MIN_SIMILARITY).order_by('-similarity')

    return qs


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows words to be viewed.
    """
    queryset = Word.objects.all().order_by('term')
    serializer_class = WordSerializer
    pagination_class = DefaultLimitOffsetPagination

    @action(detail=False)
    def near(self, request):
        query = self.request.query_params.get('q', None)
        lex = self.request.query_params.get('l', '')
        lex = lex.strip()
        mode = self.request.query_params.get('mode', MODE_STANDAR)

        queryset = search_near_dialectal(Word.objects, query, lex, mode)
        self.serializer_class = self.get_near_serializer_class(mode)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def search(self, request):
        query = self.request.query_params.get('q', None)
        lex = self.request.query_params.get('l', '')
        mode = self.request.query_params.get('mode', MODE_STANDAR)

        if query is not None:
            query = query.strip()
        lex = lex.strip()

        queryset = search_dialectal(Word.objects, query, lex, mode)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_near_serializer_class(self, mode):
        if mode in [MODE_DIALECTAL, MODE_REVERSE]:
            return EntryNearSerializer

        return WordNearSerializer
