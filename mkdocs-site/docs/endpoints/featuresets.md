# `/featuresets/`

The `/featuresets/` endpoint interacts with Tesserae's database of feature sets, which are bundles of features computed from tokens found in the literary works Tesserae has processed.  Thus, a feature set includes such features as the exact word form and the possible lemmata of a given token.  (Given that a token is an instance of a given word, the exact word form matches the word which a token is an instance of.)

## GET

Requesting GET at `/features/` provides information on features stored in Tesserae's database.

### Request

The following fields may be used in a URL query to filter the response:

|Field Name|Field Value|
|---|---|
| `form` | Only database information for the features corresponding with the specified exact word form is returned. |
| `lemma` | Only database information for features corresponding with the specified lemma is returned. |

> NB:  Remember to percent encode field values when necessary.

### Response

On success, the response includes a JSON data payload consisting of a JSON object with the key `"featuresets"`, associated with an array of JSON objects.  The JSON objects in the array, in turn, contain the following keys:

|Key|Value|
|---|---|
|`"form"`|A string matching the exact word form.|
|`"lemmata"`|A list of strings, where each string is a possible lemma for this word.|
|`"language"`|A string indicating what language this word belongs to.|

### Examples

#### Search by One Field

```
curl -i -X GET "https://tesserae.caset.buffalo.edu/featuresets/?form=leges"
```

Response:

```
HTTP/1.1 200 OK
...

{
  "featuresets": [
    {
      "form": "leges",
      "lemmata": ["lego", "lex"],
      "language": "latin"
    }
  ]
}
```

#### Search for Word Not Present in Database

```
curl -i -X GET "https://tesserae.caset.buffalo.edu/featuresets/?lemma=xlwbnd"
```

Response:

```
HTTP/1.1 200 OK
...

{
  "featuresets": []
}
```
