# `/multitexts/<uuid>/status/`

The `/multitexts/<uuid>/status/` endpoint retrieves the current status of a multitext query identified by `<uuid>`, where `<uuid>` is a placeholder for an identifying string.

## GET

Requesting GET at `/multitexts/<uuid>/status/` retrieves the status of the multitext query associated with `<uuid>`.  This association was made at the time that the multitext query was submitted with a POST at [`/multitexts/`](multitexts.md).

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

The `"status"` string can be one of the following:

|Status|Meaning|
|---|---|
|`Initialized`|The server has accepted the search and will run it when resources are available.|
|`Running`|The server is currently running the search.|
|`Done`|The server has successfully completed running the search. The search results are now available for retrieval.|
|`Failed`|An error occurred while the server was running the search.|

### Examples

#### Retrieving the Search Status of a Successfully Completed Search Job

Assume that the identifier `id1` is associated with a search job that successfully completed in 3.519 seconds.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/multitexts/id1/status/"
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

Assume that the identifier `i-failed` is associated with a failed multitext query.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/multitexts/i-failed/status/"
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

Assume that the identifier `i-expired` is not associated with any multitext results in cache.

Request:

```bash
curl -i -X GET "https://tess-new.caset.buffalo.edu/api/multitexts/i-expired/status/"
```

Response:

```http
HTTP/1.1 404 Not Found
...
```

