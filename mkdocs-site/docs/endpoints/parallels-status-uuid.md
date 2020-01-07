# `/parallels/status/<uuid>/`

The `/parallels/status/<uuid>/` endpoint retrieves the current status of a search query identified by `<uuid>`, where `<uuid>` is a placeholder for an identifying string.

## GET

Requesting GET at `/parallels/status/<uuid>/` retrieves the status of the search job associated with `<uuid>`.  This association was made at the time that the intertext query was submitted with a POST at [`/parallels/`](parallels.md).

### Request

There are no special points to note about requesting search statuses.

### Response

On success, the data payload contains a JSON object with the following keys:

|Key|Value|
|---|---|
|`"results_id"`|A string whose value equals `<uuid>`.|
|`"status"`|A string representing the current status of the search.|
|`"message"`|A string containing further details about the current status of the search.|

If the specified `<uuid>` could not be found in the database, a 404 error response will be given.  There are three scenarios in which a 404 error will occur:  (1) the specified `<uuid>` was incorrect, (2) the search job has not yet been queued, or (3) the search results have been deleted due to database maintenance.

### Examples

#### Retrieving the Search Status of a Successfully Completed Search Job

Assume that the identifier `id1` is associated with a search job that successfully completed in 3.519 seconds.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/status/id1"
```

Response:

```http
HTTP/1.1 200 OK
...
{
  "results_id": "id1",
  "status": "Done",
  "message": "Done in 3.519 seconds"
}
```

#### Retrieving the Search Status of a Failed Search Job

Assume that the identifier `i-failed` is associated with a failed search job.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/status/i-failed"
```

Response:

```http
HTTP/1.1 200 OK
...
{
  "results_id": "i-failed",
  "status": "Failed",
  "message": "Traceback (most recent call last):\n..."
}
```

#### Attempting to Retrieve a Search Status that Does Not Exist

Assume that the identifier `i-expired` is not associated with any search results in cache.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/parallels/status/i-expired"
```

Response:

```http
HTTP/1.1 404 Not Found
...
```
