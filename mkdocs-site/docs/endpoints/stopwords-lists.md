# `/stopwords/lists/`

the `/stopwords/lists` endpoint serves the names of the curated stopwords lists.  Use [`/stopwords/lists/<name>/`](stopwords-lists-name.md) to obtain one of these curated stopwords lists.

## GET

Requesting GET at `/stopwords/lists/` provides a list of strings, where each entry is the name of one of the curated stopwords lists.

### Request

There are no special points to note about requesting the curated stopwords list names.

### Response

On success, the response includes a JSON data payload consisting of a JSON object with the key `"list_names"`, associated with an array of strings.  Each string in this array is the name of a curated stopwords list available on the Tesserae database.

### Examples

#### Discover Curated Stopwords List Names

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/stopwords/lists/"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "list_names": [
    "latin-lemma-10",
    ...
  ]
}
```

## POST

> NB:  The POST method for `/stopwords/lists/` is available only on the administrative server

Requesting POST at `/stopwords/lists/` with an appropriate JSON data payload will add a stopwords list and an associated name to Tesserae's database.

### Request

Appropriate JSON data for a POST at `/stopwords/lists/` must be a JSON object containing the following keys:

|Key|Value|
|---|---|
|`"name"`|A string representing the name of the stopwords lists.|
|`"stopwords"`|An array of strings, where each string is a stopword.|

If the value given to `"name"` is already used in Tesserae's database for a stopwords list, the request will fail.  Consider a [DELETE at `/stopwords/lists/<name>/`](stopwords-lists-name.md#delete) followed by a POST at `/stopwords/lists/` if you wish to change the list associated with a given list name.

### Response

On success, the response data payload contains the key `"stopwords"` associated with an array of strings.  Additionally, the `Content-Location` header will specify the URL associated with this newly created stopwords list.

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Create a New Stopwords List

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/stopwords/lists/" -d '{ \
  "name": "new-list", \
  "stopwords": [ \
    "a", \
    "b" \
  ] \
}'
```

Response:

```http
HTTP/1.1 201 Created
...
Content-Location: /stopwords/lists/new-list/
...

{ 
  "stopwords": [
    "a",
    "b"
  ]
}
```

#### Attempt to Create a New Stopwords List with a Name Already in the Database

Suppose that `latin-lemma-10` is the name of one of the stopwords lists.

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/stopwords/lists/" -d '{ \
  "name": "latin-lemma-10", \
  "stopwords": [ \
    "a", \
    "b" \
  ] \
}'
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{ 
  "data": {
    "name": "latin-lemma-10",
    "stopwords": [
      "a",
      "b"
    ]
  }
  "message": "The stopwords list name provided (latin-lemma-10) already exists in the database. If you meant to update the stopwords list, try a DELETE at https://tess-new.caset.buffalo.edu/api/texts/latin-lemma-10/ first, then re-try this POST."
}
```

#### Attempt to Create a New Stopwords List with Insufficient Information

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/stopwords/lists/" -d '{ \
  "stopwords": [ \
    "a", \
    "b" \
  ] \
}'
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{ 
  "data": {
    "stopwords": [
      "a",
      "b"
    ]
  }
  "message": "No name provided."
}
```
