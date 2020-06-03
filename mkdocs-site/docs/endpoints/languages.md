# `/languages/`

The `/languages/` endpoint interacts with the languages registered in Tesserae's database.

## GET

Requesting GET at `/languages/` provides a list of languages.

### Request

There are no special things to do with a GET request to the `/languages/` endpoint.

### Response

On success, the response includes a data payload consisting of a JSON object with the following keys:

|Key|Value|
|---|---|
|`"languages"`|A list of strings denoting the languages found in the Tesserae database.|

### Examples

#### Retrieve Languages in the Tesserae Database

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/languages/"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "languages": [
    "greek",
    "latin"
  ]
}
```

