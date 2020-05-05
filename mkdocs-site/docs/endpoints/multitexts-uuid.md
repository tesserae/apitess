# `/multitexts/<uuid>/`

The `/multitexts/<uuid>/` endpoint serves results to multitext searches previously submitted to the `/multitexts/` endpoint.  Note that `<uuid>` is a placeholder for an identifying string.

> NB:  This endpoint is meant to be used for retrieving the results from a multitext search and not as a permanent link to a previously completed multitext search.

## GET

Requesting GET at `/multitexts/<uuid>/` retrieves the multitext search results associated with `<uuid>`.  This association was made at the time that the multitext query was submitted with a POST at [`/multitexts/`](multitexts.md).

### Request

There are no special points to note about requesting multitext search results.

### Response

On success, the data payload contains a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"multiresults"`|A list of JSON objects describing multitext results found.|

A JSON object in the `"mulitresults"` list of the successful response data payload contains the following keys:

|Key|Value|
|---|---|
|`"match_id"`|A string representing the object_id of a match in the search results used as the base of the multitext query.|
|`"bigram"`|A list containing two strings, which are a pair of matching words associated with the match associated with the value of `"match_id"`.|
|`"units"`|A list of strings, where each string represents an object_id of a unit from the corpus of texts specified in the multitext query.|
|`"scores"`|A list of numbers representing Tesserae scores of individual units.  The ith score in `"scores"` is the score of the ith unit in `"units"`.|

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
