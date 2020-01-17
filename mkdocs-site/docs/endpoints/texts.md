# `/texts/`

The `/texts/` endpoint interacts with Tesserae's database of literary works.

## GET

Requesting GET at `/texts/` provides information on literary works stored in Tesserae's database.

### Request

The following fields may be used in a URL query to filter the response:

|Field Name|Field Value|
|---|---|
| `author`|  Only database information for texts with the specified author is returned.|
| `after`|  Only database information for texts written/published after the specified year is returned; use negative integers for B.C. dates.|
| `before`|  Only database information for texts written/published before the specified year is returned; use negative integers for B.C. dates.|
| `is_prose`|  If set to "true", only database for information for texts considered prose works is returned.|
| `language`|  Only database information for texts with the specified language is returned.|
| `title`|  Only database information for texts with the specified title is returned.|

### Response

On success, the response includes a JSON data payload consisting of a JSON object with the key `"texts"`, associated with an array of JSON objects.  The JSON objects in the array, in turn, contain the following keys:

|Key|Value|
|---|---|
|`"author"`|A string identifying the text's author.|
|`"object_id"`|A string which uniquely identifies the text in the Tesserae database.|
|`"is_prose"`|A boolean value denoting whether the text is considered a prose work.|
|`"language"`|A string identifying the composition language of the text.|
|`"title"`|A string identifying the text's name.|
|`"year"`|An integer representing the text's publication year; a negative integer corresponds to the BC era.|

### Examples

#### Search by One Field

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/?author=vergil"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "texts": [
    {
      "author": "vergil",
      ...
    },
    ...
  ]
}
```

#### Search by Multiple Fields

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/?after=100&language=latin"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "texts": [
    {
      ...
      "language": "latin",
      ...
      "year": 101
    },
    ...
  ]
}
```

#### Search with No Results

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/?language=Klingon"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "texts": []
}
```

## POST

> NB:  The POST method for `/texts/` is available only on the administrative server

Requesting POST at `/texts/` with an appropriate JSON data payload will add the text described by the JSON data to Tesserae's database.

### Request

Appropriate JSON data for a POST at `/texts/` must be a JSON object containing the following keys:

|Key|Value|
|---|---|
|`"author"`|A string identifying the text's author.|
|`"is_prose"`|A boolean value denoting whether the text is a prose work.|
|`"language"`|A string identifying the composition language of the text.|
|`"path"`| A string identifying the location of the text's contents.|
|`"title"`|A string identifying the text's name.|
|`"year"`|An integer representing the text's publication year; a negative integer corresponds to the BC era.|

The JSON object is forbidden from containing the following keys: `"_id"`, `"id"`, `"object_id"`.

### Response

On success, the response data payload is a JSON object replicating the entry created in Tesserae's database according to the POST request.  Additionally, the `Content-Location` header will specify the URL associated with this newly created database entry.

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|The JSON object received as request data payload.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Upload an Entry for a Text Not in the Database

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/texts/" -d '{ \
  "author": "lucan", \
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess" \
  "language": "latin", \
  "title": "bellum civile", \
  "year": 65 \
}'
```

Response:

```http
HTTP/1.1 201 Created
...
Content-Location: /texts/5c6c69f042facf59122418f6/
...

{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "is_prose": false,
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess"
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

#### Upload an Entry for Text Not in the Database with Insufficient Information

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/texts/" -d '{ \
  "author": "lucan", \
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess" \
  "title": "bellum civile", \
  "year": 65 \
}'
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "data": {
    "author": "lucan",
    "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess"
    "title": "bellum civile",
    "year": 65
  },
  "message": "The request data payload is missing the following required key(s): language."
}
```

#### Upload an Entry for Text Not in the Database with a Prohibited Key

Request:

```bash
curl -i -X POST "https://tess-new.caset.buffalo.edu/api/texts/" -d '{ \
  "author": "lucan", \
  "object_id": "DEADBEEFDEADBEEFDEADBEEF", \
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess" \
  "language": "latin", \
  "title": "bellum civile", \
  "year": 65 \
}'
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "data": {
    "author": "lucan",
    "object_id": "DEADBEEFDEADBEEFDEADBEEF"
    "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess"
    "language": "latin",
    "title": "bellum civile",
    "year": 65
  },
  "message": "The request data payload contains the following prohibited key(s): object_id."
}
```
