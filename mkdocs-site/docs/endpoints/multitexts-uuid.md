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

A JSON object in the `"multiresults"` list contains the following keys:

|Key|Value|
|---|---|
|`"match_id"`|A string representing the object_id of a match in the search results used as the base of the multitext query.|
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
