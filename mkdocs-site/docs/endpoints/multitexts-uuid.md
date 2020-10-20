# `/multitexts/<uuid>/`

The `/multitexts/<uuid>/` endpoint serves results to multitext searches previously submitted to the `/multitexts/` endpoint.  Note that `<uuid>` is a placeholder for an identifying string.

> NB:  This endpoint is meant to be used for retrieving the results from a multitext search and not as a permanent link to a previously completed multitext search.

## GET

Requesting GET at `/multitexts/<uuid>/` retrieves the multitext search results associated with `<uuid>`.  This association was made at the time that the multitext query was submitted with a POST at [`/multitexts/`](multitexts.md).

### Request

By default, all results of the multitext search will be returned on request.

To restrict the results returned (e.g., for displaying purposes), the following URL query strings may be used:

If provided, the URL query string must have the following keys and values:

|Key|Value|
|---|---|
|`sort_by`|Either `score`, `source_tag`, or `target_tag`.|
|`sort_order`|Either `ascending` or `descending`.|
|`per_page`|Any positive integer, specifying the maximum number of original Tesserae results requested.|
|`page_number`|Any non-negative integer, with the first page starting at 0.|

Note that these paging options correspond to the results from the original
Tesserae search on which this multitext search is based. For more information on how these URL query strings are used to restrict the original search results retrieved,
see [`/parallels/<uuid>/`](parallels-uuid.md).

### Response

On success, the data payload contains a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"max_score"`|The highest score of all results from the original Tesserae search on which this multitext search is based.|
|`"total_count"`|The total number of parallels found in the original Tesserae search on which this multitext search is based.|
|`"multiresults"`|A list of JSON objects describing multitext results found.|

A JSON object in the `"multiresults"` list contains the following keys:

|Key|Value|
|---|---|
|`"match"`|A JSON object representing a match in the search results used as the base of the multitext query. See [Get Response for `/parallels/<uuid>/`](parallels-uuid.md#response) for more details.|
|`"cross-ref"`|A list containing JSON objects representing multitext search result information.|

A JSON object in the `"cross-ref"` list contains the following keys:

|Key|Value|
|---|---|
|`"bigram"`|A list containing two strings, which are a pair of matching words associated with the match associated with the value of `"match_id"`.|
|`"units"`|A list of JSON objects, where each JSON object represents a unit from the corpus of texts specified in the multitext query.|

A JSON object in the `"units"` list contains the following keys:

|Key|Value|
|---|---|
|`"unit_id"`|A string representing the object_id of the unit.|
|`"tag"`|A string representing the locus of the unit.|
|`"snippet"`|A string representing displaying the text of the unit.|
|`"score"`|A number representing the Tesserae score of the unit.|

> NB:  A successful response body will be compressed with gzip.

On failure, the response is a 404 error.

### Examples

#### Retrieving Multitext Results

Assume that the identifier `id1` is associated with a certain multitext result.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/multitexts/id1"
```

Response:

```http
HTTP/1.1 200 OK
...
Content-Encoding: gzip
...

...
```

(If you would like to actually download the gzipped file, try `curl -o id1.json.gz "https://tess-new.caset.buffalo.edu/api/multitexts/id1/"`)

#### Attempting to Retrieve Search Results that Do Not Exist

Assume that the identifier `i-expired` is not associated with any multitext results in cache.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/multitexts/i-expired"
```

Response:

```http
HTTP/1.1 404 Not Found
...
```
