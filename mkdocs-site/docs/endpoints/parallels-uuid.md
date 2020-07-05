# `/parallels/<uuid>/`

The `/parallels/<uuid>/` endpoint serves the results from a Tesserae intertext discovery run.  Note that `<uuid>` is a placeholder for an identifying string.

> NB:  This endpoint is meant to be used for retrieving the results from a Tesserae search and not as a permanent link to a previously completed search.

## GET

Requesting GET at `/parallels/<uuid>/` retrieves the Tesserae search results associated with `<uuid>`.  This association was made at the time that the intertext query was submitted with a POST at [`/parallels/`](parallels.md).

### Request

It is possible to request Tesserae search results either with a URL query string to restrict the results returned in the response or without a URL query string to return all results of the search.

If provided, the URL query string must have the following keys and values:

|Key|Value|
|---|---|
|`sort_by`|Either `score`, `source_tag`, `target_tag`, or `matched_features`.|
|`sort_order`|Either `ascending` or `descending`.|
|`per_page`|Any positive integer, specifying the maximum number of results requested.|
|`page_number`|Any non-negative integer, with the first page starting at 0.|

### Response

On success, the data payload contains a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"max_score"`|The highest score of all results associated with the UUID.|
|`"total_count"`|The total number of parallels associated with the UUID.|
|`"parallels"`|A list of JSON objects describing parallels found.|

A JSON object in the `"parallels"` list of the successful response data payload contains the following keys:

|Key|Value|
|---|---|
|`"object_id"`|A string representing the database identifier for this parallel.|
|`"source_tag"`|A string representing the text span used as the source in this parallel.|
|`"target_tag"`|A string representing the text span used as the target in this parallel.|
|`"matched_features"`|A list of strings, where each string represents a feature found in both the source span and the target span.|
|`"score"`|A number representing the score assigned to the pair of text spans.|
|`"source_snippet"`|The string making up the text span specified by the value of `"source"`.|
|`"target_snippet"`|The string making up the text span specified by the value of `"target"`.|
|`"highlight"`|Information to highlight areas on the source and target spans used to determine the score.|

> NB:  A successful response body will be compressed with gzip.

Failure can be due either to a mistake in the URL query string or because the resource does not exist. If there is a mistake in the URL query string, a 400 error will be returned, along with a JSON object containing the following keys:

|Key|Value|
|---|---|
|`"data"`|A JSON object associating the URL query keys received with the request, along with the query values.|
|`"message"`|An error message indicating the first mistake encountered in the URL query string.|

In the case of a resource not exististing (including those which will exist in the future, but only after successful processing), a 404 error will be returned.

### Examples

#### Retrieving All Search Results

Assume that the identifier `id1` is associated with a certain search result.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/id1/"
```

Response:

```http
HTTP/1.1 200 OK
...
Content-Encoding: gzip
...

...
```

#### Retrieving the Top 100 Search Results by Score

Assume that the identifier `id1` is associated with a certain search result.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/id1/?sort_by=score&sort_order=descending&per_page=100&page_number=0"
```

Response:

```http
HTTP/1.1 200 OK
...
Content-Encoding: gzip
...

...
```

#### Forgetting a URL Query Key

Assume that the identifier `id1` is associated with a certain search result.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/id1/?sort_by=score&sort_order=descending&per_page=100"
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "data": {
    "sort_by": "score",
    "sort_order": "descending",
    "per_page": "100"
  },
  "message": "The request data payload is missing the following required key(s): page_number"
}
```

#### Using an Unsupported URL Query Value

Assume that the identifier `id1` is associated with a certain search result.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/id1/?sort_by=score&sort_order=descending&per_page=100&page_number=-5"
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "data": {
    "sort_by": "score",
    "sort_order": "descending",
    "per_page": "100",
    "page_number": "-5"
  },
  "message": "Specified \"page_number\" value (-5) is not supported. Only non-negative integers are supported."
}
```

#### Attempting to Retrieve Search Results that Do Not Exist

Assume that the identifier `i-expired` is not associated with any search results in cache.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/i-expired/"
```

Response:

```http
HTTP/1.1 404 Not Found
...
```
