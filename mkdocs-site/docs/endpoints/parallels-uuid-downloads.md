# `/parallels/<uuid>/downloads/`

The `/parallels/<uuid>/downloads/` endpoint permits downloading of the results from a Tesserae intertext discovery run.  Note that `<uuid>` is a placeholder for an identifying string.

> NB:  This endpoint is meant to be used for retrieving the results from a Tesserae search and not as a permanent link to a previously completed search's results.

## GET

Requesting GET at `/parallels/<uuid>/downloads/` retrieves the Tesserae search results associated with `<uuid>`.  This association was made at the time that the intertext query was submitted with a POST at [`/parallels/`](parallels.md).

### Request

There are no special things to do with a GET request to the `/parallels/<uuid>/downloads/` endpoint.

### Response

On success, the response body will be a tab-delimited file containing the results of the search associated with `<uuid>`.

A 404 Not Found error indicates one of two possibilities. One is that the specified `<uuid>` does not exist in the database. The other is that the results associated with `<uuid>` are not yet ready for download. In either case, the [`/parallels/<uuid>/status/`](parallels-uuid-status.md) endpoint may be helpful.
