
# API Endpoints

## Pagination
Implemented using django-rest-framework [`LimitOffsetPagination`](https://www.django-rest-framework.org/api-guide/pagination/#limitoffsetpagination)
`limit`: indicates the maximum number of items to return, and is equivalent to the page_size in other styles.
`offset`: indicates the starting position of the query in relation to the complete set of unpaginated items.

GET /api/gramcats/?limit=10&offset=30


## Words
### Search word: /api/words/search/

`q`: query string
`l`: lexicon to select (always `es-ca`)
`mode`: provides the language of parameter `q` that will be search on the lexicon
    - `standar`: query string is in the source language of the lexicon. E.g. if lexicon is `es-ca` it is `es` (Spanish).
    - `reverse`: query string is in the destination language of the lexicon. E.g. if lexicon is `es-ca` it is `ca` (Catalan).
    - `dialectal`: query string string is in a diatopic variation of the destination language. E.g. if lexicon is `es-ca`it is a Diatopic Variation of Catalan.


Examples of use:
`/api/words/search/?q=golondrina&l=es-ca&mode=standar`
`/api/words/search/?q=oreneta&l=es-ca&mode=reverse`
`/api/words/search/?q=orineta&l=es-ca&mode=dialectal`

The three requests return the same result, check [`api_words_search.json`](api_words_search.json)

### Word detail: /api/words/<id>/
`id`: identifier of the word. E.g. 1234

See sample output on [`api_words_detail.json`](api_words_detail.json)

## Gramatical categories
### /api/gramcats/
List all existing categories.
```
GET /api/gramcats/?offset=60&limit=2`
```
```json
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 79,
    "next": "http://127.0.0.1:1234/api/gramcats/?limit=2&offset=62",
    "previous": "http://127.0.0.1:1234/api/gramcats/?limit=2&offset=58",
    "results": [
        {
            "abbreviation": "s. inv.",
            "title": "sustantivo invariable"
        },
        {
            "abbreviation": "s. m.",
            "title": "sustantivo masculino"
        }
    ]
}
```

