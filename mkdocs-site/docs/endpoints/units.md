# `/units/`

The `/units/` endpoint interacts with the units registered in Tesserae's database.

## GET

Requesting GET at `/units/` provides a list of units.  How this list of units was created is dependent on the URL query fields used.

By default, a GET at `/units/` returns an empty list.

### Request

The following fields may be used in a URL query to specify the parameters by which the list of units is created:

|Field Name|Field Value|
|---|---|
|`unit_type`|A string refering to a unit type ("line" or "phrase").|
|`works`|A percent-encoded string of the form `<object_id 1>,<object_id 2>,...`, specifying which works' units are to be retrieved.|

### Response

On success, the response includes a data payload consisting of a JSON object with the following keys:

|Key|Value|
|---|---|
|`"units"`|A list of JSON objects representing units.|

Each JSON object in the list referenced by `"units"` in the response object has the following keys:

|Key|Value|
|---|---|
|`"index"`|An integer denoting the order in which this unit appears in the text.|
|`"snippet"`|A display string for the unit.|
|`"tags"`|A list of strings matching the tag information on the line(s) of the .tess file from which this unit was extracted.|
|`"text"`|A string representing the identifier for the text to which this unit belongs.|
|`"tokens"`|A list of JSON objects representing word tokens found in the unit.  Further detail is found below.|
|`"unit_type"`|A string representing the type of this unit ("line" or "phrase").|

Each JSON object in the `"tokens"` list has the following keys:

|Key|Value|
|---|---|
|`"index"`|An integer denoting the order in which this token appears in the text.|
|`"display"`|A string showing how the token appeared in the text.|
|`"features"`|A JSON object associating a feature type with a list of feature indices.|

### Examples

#### Retrieve Units from a Particular Text

Suppose that `5c6c69f042facf59122418f6` is an identifier for a text in the database.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/units/?works=5c6c69f042facf59122418f6"
```

Response:

```http
HTTP/1.1 200 OK
...

{
  "units": [
    {
      "index": 0,
      "snippet": "lorem ipsum",
      "tags": ["1.1"]
      "text": "5c6c69f042facf59122418f6",
      "tokens": [
        {
          "index": 0,
          "display": "lorem",
          "features": {
            "form": [0],
            "lemmata": [0, 1]
          }
        },
        {
          "index": 2,
          "display": "ipsum",
          "features": {
            "form": [1],
            "lemmata": [2]
          }
        }
      ]
      "unit_type": "line"
    },
    {
      "index": 1,
      ...
    },
    ...
  ]
}
```
