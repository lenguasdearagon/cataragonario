from django.contrib.postgres.search import TrigramSimilarity
from django.http.response import HttpResponse
from linguatec_lexicon.models import Word, WordManager
from linguatec_lexicon.serializers import WordSerializer
from linguatec_lexicon.views import DefaultLimitOffsetPagination
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response



MODE_DIALECTAL = 'dialectal'
MODE_REVERSE = 'reverse'
MODE_STANDAR = 'standar'

SEARCH_MODES = (MODE_STANDAR, MODE_REVERSE, MODE_DIALECTAL)



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
    def search(self, request):
        query = self.request.query_params.get('q', None)
        lex = self.request.query_params.get('l', '')
        mode = self.request.query_params.get('mode', 'standar')

        if query is not None:
            query = query.strip()
        lex = lex.strip()


        queryset = search_dialectal( Word.objects, query, lex, mode)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    # # TODO(@slamora)
    # @action(detail=False)
    # def near(self, request):
    #     return Response()
