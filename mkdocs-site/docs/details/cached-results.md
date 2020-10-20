# Cached Results

This page describes expected server behavior with respect to Tesserae search results.

## Context

A Tesserae search occurs when Tesserae is given a set of text spans in which to search for intertexts with another set of text spans, according to some set of parameters.  The results of this search, then, will always be the same given the same sets of text spans and set of parameters.  Thus, it is possible to save the results in cache (i.e., cache the results) so that when the same sets of texts and same set of parameters are given, the same results can be returned without repeating the work.

## Expiration of Cache

It is normal policy to purge cached items if they are not requested for some period of time.  Since the same results could be obtained again based on the same sets of text spans and set of parameters, the only difference between retrieving from cache and re-computing the results is the time it takes to obtain a response (re-computing will take longer).

Additionally, items retrieved more often from cache are more likely to remain in cache.

The current policy for Tesserae's official deployment of the TIS-API is to automatically delete cached search results after one year of not being retrieved, though server maintenance may cause cache deletion earlier than that.

## Problems with Results as Resource

Although it is also possible to directly query for the results using the [`/parallels/<uuid>/`](../endpoints/parallels-uuid.md) endpoint, this is discouraged.  Because results are occasionally purged, they may no longer exist as resources.  As a result, it is possible to receive a 404 error for results obtained in the past.  For this reason, it is recommended that API users re-submit Tesserae searches.  If the results are still in cache, the redirect response will come almost immediately; otherwise, the redirect response will come after the results are computed.  In either case, the URL provided for the redirect is guaranteed to contain the search results.

## Compression of Results

Because there may be many matches within a search result and redundant information can be present, search results utilize the gzip compression algorithm to reduce the size of transferred information.
