# `/stopwords/`

The `/stopwords/` endpoint serves stopwords lists.  These lists can be useful when parameterizing the scoring algorithm at the `/parallels/` endpoint.

Stopwords lists are typically computed using frequency information.  The reasoning is that the most frequent features are typically the least informative (consider, for example, the articles in English).

Of course, depending on your needs, you may choose to exclude certain words recommended by the `/stopwords/` endpoint or include words that were not recommended.
These decisions can be made when specifying stopwords in your application.

## GET

Requesting GET at `/stopwords/` provides a JSON object containing a stopwords list.  How this stopwords list was created is dependent on the URL query fields used.

By default, a GET at `/stopwords/` returns a JSON object containing an empty list.

### Request

The following fields may be used in a URL query to specify the parameters by which the stopwords list is created:

|Field Name|Field Value|
|---|---|
|`feature`|A string specifying the linguistic feature by which frequencies are calculated; `lemmata` is the default.|
|`list_size`|An integer specifying the number of stopwords to include in the stopwords list. `10` is the default.|
|`language`|A string specifying one of the languages in the Tesserae database; all works in that language will be used to determine feature frequencies.|
|`works`|A percent-encoded string of the form `<object_id 1>,<object_id 2>,...`, specifying which works are used to determine feature frequencies.|

In the case that both `works` and `language` are specified, the `language` option will take precedence.

### Response

On success, the response data payload will contain a JSON object with the key `"stopwords"`, associated with a list of strings.

On failure, the data payload contains error information in a JSON object with the following keys:

|Key|Value|
|---|---|
|`"data"`|A JSON object whose keys are the received URL query fields, associated with percent-decoded values.|
|`"message"`|A string explaining why the request data payload was rejected.|

### Examples

#### Get the 10 Highest Frequency Lemmata in Latin

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/stopwords/?language=latin"
```

Response:

```http
HTTP/1.1 200 OK
...

{ 
  "stopwords": [
    ...
  ]
}
```

#### Get the 20 Highest Frequency Lemmata in Latin

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/stopwords/?language=latin&list_size=20"
```

Response:

```http
HTTP/1.1 200 OK
...

{ 
  "stopwords": [
    ...
  ]
}
```

#### Get the 15 Highest Frequency Lemmata in Two Specific Texts

Assume that `5c6c69f042facf59122418f6` and `5c6c69f042facf59122418f8` are object IDs of texts in the database.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/stopwords/?works=5c6c69f042facf59122418f6%2C5c6c69f042facf59122418f8&list_size=15"
```

Response:

```http
HTTP/1.1 200 OK
...

{ 
  "stopwords": [
    ...
  ]
}
```

#### Attempt to Get a Stopwords List with a Text Not in the Database

Suppose no text has the identifier `DEADBEEFDEADBEEFDEADBEEF`.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/stopwords/?works=DEADBEEFDEADBEEFDEADBEEF&list_size=15"
```

Response:

```http
HTTP/1.1 400 Bad Request
...

{
  "data": {
    "works": ["DEADBEEFDEADBEEFDEADBEEF"],
    "list_size": 15
  },
  "message": "No text can be found with the identifier provided (DEADBEEFDEADBEEFDEADBEEF)."
}
```
