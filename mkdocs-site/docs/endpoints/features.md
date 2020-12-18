# `/features/`

The `/features/` endpoint interacts with features registered in Tesserae's database.

## GET

Requesting GET at `/features/` provides a JSON object containing a list of features.  How this list of features was created is dependent on the URL query fields used.

By default, a GET at `/features/` returns a JSON object containing an empty list.

### Request

The following fields may be used in a URL query to filter the response:

|Field Name|Field Value|
|---|---|
| `language` | Limits features retrieved to be of the specified language. |
| `feature` | Limits features retrieved to be of the specified feature type. |
| `token` | Limits features retrieved to be of the specified representation. |

> NB:  Remember to percent encode field values when necessary.

### Response

On success, the response includes a JSON data payload consisting of a JSON object with the key `"features"`, associated with an array of JSON objects.  The JSON objects in the array, in turn, contain the following keys:

|Key|Value|
|---|---|
|`"language"`|A string indicating what language this feature belongs to.|
|`"feature"`|A string representing the feature type of this feature.|
|`"token"`|A string representing this feature.|
|`"index"`|An integer denoting the order in which the database became aware of this feature, relative to other instances of this feature type for the given language.|
|`"frequencies"`|A JSON object associating text identifiers with the number of instances this feature occurs in that text.|

### Examples

#### Search by One Field

Suppose that "lego" is the 45th Latin form and the 67th Latin lemma the database encountered.

```bash
curl -i -X GET "https://tesserae.caset.buffalo.edu/api/features/?token=lego"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "features": [
    {
      "language": "latin",
      "feature": "form",
      "token": "lego",
      "index": 45,
      "frequencies": { ... }
    },
    {
      "language": "latin",
      "feature": "lemmata",
      "token": "lego",
      "index": 67,
      "frequencies": { ... }
    },
    ...
  ]
}
```

#### Search for Feature Not Present in Database

```bash
curl -i -X GET "https://tesserae.caset.buffalo.edu/api/features/?token=xlwbnd"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "features": []
}
```

#### Retrieve Features of a Feature Type for a Language

```bash
curl -i -X GET "https://tesserae.caset.buffalo.edu/api/features/?feature=lemmata&language=latin"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "features": [
    {
      "language": "latin",
      "feature": "lemmata",
      ...
    },
    {
      "language": "latin",
      "feature": "lemmata",
      ...
    },
    ...
  ]
}
```
