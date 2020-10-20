# `/parallels/<uuid>/`

The `/parallels/<uuid>/` endpoint serves the results from a Tesserae intertext discovery run.  Note that `<uuid>` is a placeholder for an identifying string.

> NB:  This endpoint is meant to be used for retrieving the results from a Tesserae search and not as a permanent link to a previously completed search.

## GET

Requesting GET at `/parallels/<uuid>/` retrieves the Tesserae search results associated with `<uuid>`.  This association was made at the time that the intertext query was submitted with a POST at [`/parallels/`](parallels.md).

### Request

By default, all results of the search will be returned on request.

To restrict the results returned (e.g., for displaying purposes), the following URL query string may be used:

|Key|Value|
|---|---|
|`sort_by`|Either `score`, `source_tag`, or `target_tag`.|
|`sort_order`|Either `ascending` or `descending`.|
|`per_page`|Any positive integer, specifying the maximum number of results requested.|
|`page_number`|Any non-negative integer, with the first page starting at 0.|

Note that if any one of these URL query strings is used, all the other must also be used to prevent an error response.
`sort_by` and `sort_order` define the ordering in which to consider the search results.
`per_page` and `page_number` are used to navigate the results according to the previously specified ordering.
For example, if `sort_by` were set to `score` and `sort_order` to `descending`, the results were would be ordered by score, from highest to lowest.
Then, by setting `per_page` to `10` and `page_number` to `0`, a GET request would retrieve the 10 highest scoring results.
Incrementing `page_number` to `1` and leaving all of the other arguments as before would retrieve the next 10 highest scoring results.
When the combination used by `per_page` and `page_number` reaches the end of the results, the last of the results will be returned.
If the combination of `per_page` and `page_number` requests a result beyond the end of the results, no results are returned.

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
|`"source_snippet"`|The string from the source text in which this particular parallel was found.|
|`"target_snippet"`|The string from the target text in which this particular parallel was found.|
|`"highlight"`|A list of list of integers indicating which part of the source and target texts held matching features. In particular, the first level of the list of lists encapsulates all matches found, and the second level of the list of lists refers to a specific match found: the first integer indicates the token position in the string associated with `"source_snippet"` in which a feature was found and the second integer indicates the token position in the string associated with `"target_snippet"` in which the same feature was found.|

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
