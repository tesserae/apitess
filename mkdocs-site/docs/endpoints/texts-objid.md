# `/texts/<object_id>/`

The `/texts/<object_id>/` endpoint interacts with a specific literary work in Tesserae's database.

Note that `<object_id>` is a placeholder to be replaced by an identifier refering to a specific text (i.e., literary work).  Throughout the rest of this page, `<object_id>` will continue to serve as a placeholder for a text's identifier.

## GET

Requesting GET at `/texts/<object_id>/` provides information on the literary work specified by `<object_id>`.

### Request

Note that an `<object_id>` used for one text on the Tesserae website may be different from the `<object_id>` used to refer to the same text on a different instance of Tesserae (such as one locally installed on your computer).

### Response

On success, the response includes a data payload consisting of a JSON object with the following keys:

|Key|Value|
|---|---|
|`"author"`|A string identifying the text's author.|
|`"object_id"`|A string which uniquely identifies the text on the instance of Tesserae you queried.|
|`"language"`|A string identifying the composition language of the text.|
|`"title"`|A string identifying the text's name.|
|`"year"`|An integer representing the text's publication year; a negative integer corresponds to the BC era.|

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"object_id"`|A string corresponding to `<object_id>`.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Retrieve a Text's Database Entry

Suppose that `5c6c69f042facf59122418f6` is the identifier associated with Lucan's *Bellum Civile*.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/5c6c69f042facf59122418f6/"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

#### Attempt to Retrieve a Database Entry with a Malformed `object_id`

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/badid/"
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "object_id": "badid",
  "message": "Provided identifier (badid) is malformed."
}
```

#### Attempt to Retrieve the Database Entry for a Text Not in the Database

Assume that no text in the database has the identifier "DEADBEEFDEADBEEFDEADBEEF".

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/texts/DEADBEEFDEADBEEFDEADBEEF/"
```

Response:

```http
HTTP/1.1 404 Not Found
...

{
  "object_id": "DEADBEEF",
  "message": "No text with the provided identifier (DEADBEEFDEADBEEFDEADBEEF) was found in the database."
}
```

## PATCH

> NB:  The PATCH method for `/texts/<object_id>/` is available only on the administrative server

Requesting PATCH at `/texts/<object_id>/` with an appropriate JSON data payload will update the database entry of the text with an identifier of `<object_id>`.  The update will be in accordance with the JSON data.

### Request

Appropriate JSON data for a PATCH at `/texts/<object_id>/` is any JSON object without the following keys:  `"object_id"`, `"id"`, `"_id"`, `"path"`, `"divisions"`.  The keys in this object specify which attributes of the text entry in Tesserae's database will be updated (or added, if the key does not correspond with any of the text entry's attributes).  The new values of these attributes are specified by the values of the keys corresponding to those attributes.

> NB:  You cannot update a text's identifier.

### Response

On success, the data payload contains the text entry in Tesserae's database after the update has been made.

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"object_id"`|A string matching `<object_id>`.|
|`"data"`|The JSON object received as request data payload.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Update the Value of a Pre-existing Attribute of a Text's Database Entry

Assume that the following entry exists in the database:

```json
{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

Request:

```bash
curl -i -X PATCH "https://tess-new.caset.buffalo.edu/api/texts/5c6c69f042facf59122418f6/" -d '{ \
  "title": "Pharsalia" \
}'
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "Pharsalia",
  "year": 65
}
```

#### Add New User-Specified Information to a Text's Database Entry

Assume that the following entry exists in the database:

```json
{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

Request:

```bash
curl -i -X PATCH "https://tess-new.caset.buffalo.edu/api/texts/5c6c69f042facf59122418f6/" -d '{ \
  "alternate_title": "Pharsalia" \
}'
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "alternate_title": "Pharsalia"
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

#### Attempt to Update a Database Entry with a Malformed `object_id`

Request:

```bash
curl -i -X PATCH "https://tess-new.caset.buffalo.edu/api/texts/badid/" -d '{ \
  "fail": "this example will" \
}'
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "object_id": "badid",
  "data": {
    "fail": "this example will"
  },
  "message": "Provided identifier (badid) is malformed."
}
```

#### Attempt to Update the Database Entry for a Text Not in the Database

Assume that no text in the database has the identifier "DEADBEEFDEADBEEFDEADBEEF".

Request:

```bash
curl -i -X PATCH "https://tess-new.caset.buffalo.edu/api/texts/DEADBEEFDEADBEEFDEADBEEF/" -d '{ \
  "fail": "this example will" \
}'
```

Response:

```http
HTTP/1.1 404 Not Found
...

{
  "object_id": "DEADBEEFDEADBEEFDEADBEEF",
  "data": {
    "fail": "this example will"
  },
  "message": "No text with the provided identifier (DEADBEEFDEADBEEFDEADBEEF) was found in the database."
}
```

## DELETE

> NB:  The DELETE method for `/texts/<object_id>/` is available only on the administrative server

Requesting DELETE at `/texts/<object_id>/` will delete the text identified by `<object_id>` from Tesserae's database.

### Request

There is no request data payload.

### Response

On success, there is no response data payload.

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"object_id"`|A string matching `<object_id>`.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Delete a Text

Assume that the following entry exists in the database:

```json
{
  "author": "lucan",
  "object_id": "5c6c69f042facf59122418f6",
  "path": "https://raw.githubusercontent.com/tesserae/tesserae/master/texts/la/lucan.bellum_civile.tess",
  "language": "latin",
  "title": "bellum civile",
  "year": 65
}
```

Request:

```bash
curl -i -X DELETE "https://tess-new.caset.buffalo.edu/api/texts/5c6c69f042facf59122418f6/"'
```

Response:

```http
HTTP/1.1 204 No Content
...
```

#### Attempt to Delete a Database Entry with a Malformed `object_id`

Request:

```bash
curl -i -X DELETE "https://tess-new.caset.buffalo.edu/api/texts/badid/"
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "object_id": "badid"
  "message": "Provided identifier (badid) is malformed."
}
```

#### Attempt to Delete a Database Entry for a Text Not in the Database

Assume that no text in the database has the identifier "DEADBEEFDEADBEEFDEADBEEF".

Request:

```bash
curl -i -X DELETE "https://tess-new.caset.buffalo.edu/api/texts/DEADBEEFDEADBEEFDEADBEEF/"
```

Response:

```http
HTTP/1.1 404 Not Found
...

{
  "object_id": "DEADBEEFDEADBEEFDEADBEEF"
  "message": "No text with the provided identifier (DEADBEEFDEADBEEFDEADBEEF) was found in the database."
}
```
