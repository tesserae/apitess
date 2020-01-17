# `/tokens/`

The `/tokens/` endpoint interacts with the tokens registered in Tesserae's database.

## GET

Requesting GET at `/tokens/` provides a JSON object containing a list of tokens.  How this list of tokens was created is dependent on the URL query fields used.

By default, a GET at `/tokens/` returns a JSON object containing an empty list.

### Request

The following fields may be used in a URL query to specify the parameters by which the list of tokens is created:

|Field Name|Field Value|
|---|---|
|`works`|A percent-encoded string of the form `<object_id 1>,<object_id 2>,...`, specifying which works' tokens are to be retrieved.|

### Response

On success, the response includes a data payload consisting of a JSON object with the following keys:

|Key|Value|
|---|---|
|`"tokens"`|A list of JSON objects representing tokens.|

Each JSON object in the list referenced by `"tokens"` in the response object has the following keys:

|Key|Value|
|---|---|
|`"text"`|A string representing the identifier for the text to which this token belongs.|
|`"index"`|An integer denoting the order in which this token appears in the text.|
|`"display"`|A string showing how the token appeared in the text.|

### Examples

#### Retrieve Tokens from a Particular Text

Suppose that `5c6c69f042facf59122418f6` is an identifier for a text in the database.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/tokens/?works=5c6c69f042facf59122418f6"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "tokens": [
    {
      "text": "5c6c69f042facf59122418f6",
      "index": 0,
      "display": ...
    },
    {
      "text": "5c6c69f042facf59122418f6",
      "index": 1,
      "display": ...
    },
    ...
  ]
}
```
