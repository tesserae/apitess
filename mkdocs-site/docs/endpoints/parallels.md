# `/parallels/`

The `/parallels/` endpoint interacts with Tesserae's intertext discovery capabilities.

## POST

Requesting POST at `/parallels/` submits a query for discovering intertexts between the texts available in Tesserae's database.  The query parameters should be sent as a JSON data payload.

### Request

The JSON data payload representing query parameters must contain the following keys.

|Key|Value|
|---|---|
|`"source"`|A JSON object describing source units.  Further details are available at [Units](../details/units.md).  These units will be compared with the units described by `"target"` to find intertexts.|
|`"target"`|A JSON object describing target units.  Further details are available at [Units](../details/units.md).  These units will be compared with the units described by `"source"` to find intertexts.|
|`"method"`|A JSON object describing the scoring method used to evaluate the intertextual strength of a source text and target text pair.  More information on specifying the scoring method can be found in [Scoring Methods](../details/methods.md).|

### Response

On success, one of two responses will be returned.  The first is a 201 (created); the second is a 303 (see other).  In either case, a `Location` header will specify the URL where the search results can be retrieved.  Note that the URL specified in the `Location` header will conform to the [`/parallels/<uuid>/`](parallels-uuid.md) endpoint.

The distinction between the two successful responses is a matter of whether the search results remain cached in the database.  If the search results are not in cache at the time of the request, a 201 response is given, and the results, once the search is complete, are cached.  If the search results are in cache at the time of the request, a 303 response is given and a URL identical to the one served when put into cache is served.  For more details, see [Cached Results](../details/cached-results.md).

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Submit a Tesserae Search

Request:

```bash
curl -i -X POST -H "Content-Type: application/json; charset=utf-8" \
"https://tess-new.caset.buffalo.edu/api/parallels/" \
--data-binary @- << EOF
{
  "source": {
    "object_id": "5c6c69f042facf59122418f8",
    "units": "line"
  },
  "target": {
    "object_id": "5c6c69f042facf59122418f6",
    "units": "line"
  },
  "method": {
    "name": "original",
    "feature": "lemmata",
    "stopwords": [
      "qui", "quis", "sum", "et", "in",
      "is", "non", "hic", "ego", "ut"
    ],
    "freq_basis": "corpus",
    "max_distance": 10,
    "distance_basis": "frequency"
  }
}
EOF
```

Response:

```http
HTTP/1.1 201 Created
...
Location: /parallels/some-uuid-for-results/
...
```
