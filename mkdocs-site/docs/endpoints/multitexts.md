# `/multitexts/`

The `/multitexts/` endpoint interacts with Tesserae's multitext functionality, which allows users to explore the question, "Given a set of intertexts previously found through Tesserae, how frequently do similar matching words for each of those intertexts occur in a given corpus?"

## POST

Requesting POST at `/multitexts/` submits a query for discovering units of a specified corpus that match with intertexts previously found through Tesserae at the `/parallels/` endpoint.

### Request

The JSON data payload representing query parameters must contain the following keys.

|Key|Value|
|---|---|
|`"parallels_uuid"`|A string UUID corresponding to the results of a previously completed intertext discovery query submitted at the [`/parallels/` endpoint](parallels.md).|
|`"text_ids"`|A list of strings corresponding to `object_id`s of texts in Tesserae's database.|
|`"unit_type"`|A string describing the units by which to look through the specified texts.  It should either by "line" or "phrase".  For specified texts that are prose works, this option is ignored (prose works are looked at by phrase only).|

### Response

On success, one of two responses will be returned.  The first is a 201 (created); the second is a 303 (see other).  In either case, a `Location` header will specify the URL where the multitext results can be retrieved.  Note that the URL specified in the `Location` header will conform to the [`/multitexts/<uuid>/`](multitexts-uuid.md) endpoint.

The distinction between the two successful responses is a matter of whether the multitext results remain cached in the database.  If the multitext results are not in cache at the time of the request, a 201 response is given, and the results, once processing is complete, are cached.  If the multitext results are in cache at the time of the request, a 303 response is given and a URL identical to the one served when put into cache is served.  For more details, see [Cached Results](../details/cached-results.md).

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

##### Submit a multitext search

Request:

```bash
curl -i -X POST  -H "Content-Type: application/json; charset=utf-8" \
"https://tesserae.caset.buffalo.edu/api/multitext/" \
--data-binary @- << EOF
{
  "parallels_uuid": "uuid-to-previous-search-results",
  "text_ids": [
    "id-for-text-1",
    "id-for-text-2",
    ...
  ],
  "unit_type": "line"
}
EOF
```

Response:

```http
HTTP/1.1 201 Created
...
Location: /multitexts/some-uuid-for-results/
...
```
