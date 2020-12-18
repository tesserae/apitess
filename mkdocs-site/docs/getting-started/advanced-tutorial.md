# Advanced Tutorial

This page presents more advanced concepts than what was presented in [the tutorial](tutorial.md).  It will require access to a Unix terminal.

By the end of this advanced tutorial, you should be able to use the TIS API to obtain Tesserae search results.

## Tesserae Search

The main service that Tesserae provides is its intertext discovery capabilities.
In order for Tesserae to make these discoveries, it needs restrictions on where and how it will look for intertexts.
Among the restrictions to constrain where Tesserae looks for intertexts are options such as which work to use as the source text and which work to use as the target text.
Furthermore, we may already know of some words that we would like to exclude from counting as evidence for an intertextual relation between units of the source and target texts.
The TIS API allows for specifying these restrictions (among others), which allows us to submit Tesserae search queries through the TIS API.

For purposes of this tutorial, we will use the TIS API to obtain the intertexts between Vergil's *Aeneid* and Lucan's *Bellum Civile*.
If we wish to use the TIS API to retrieve those intertexts, we must first craft a search query that specifies our constraints.
Then, we must submit the query and wait for Tesserae to complete processing the query.
Finally, we can retrieve the results and inspect the matches Tesserae found.

## Submitting a Query at the `/parallels/` Endpoint

In order to submit a Tesserae search query, we must use the URL <https://tesserae.caset.buffalo.edu/api/parallels/> (if you use your web browser to GET that URL, you'll probably see a blank page or an error message).
If you were following along from [the tutorial](tutorial.md), you have probably noticed that the URL for submitting a query and for looking at the texts available through the TIS API are very similar.
In fact, if we line up the URLS:

  * <https://tesserae.caset.buffalo.edu/api/texts/>
  * <https://tesserae.caset.buffalo.edu/api/parallels/>

you can see that they are identical except for the last part of the URL, where one ends in `/texts/` and the other ends in `/parallels/`.
Thus, the TIS API has a `/texts/` endpoint for obtaining texts available through the TIS API and a `/parallels/` endpoint for submitting Tesserae search queries.

Unlike the `/texts/` endpoint, the `/parallels/` endpoint does not respond to a GET request.
Instead, the `/parallels/` endpoint expects a POST request.
Like GET, POST is one of the HTTP methods.
Unlike GET, POST allows the client to submit more than just the URL to the server; POST allows the client to provide the server with extra data.
The TIS API is defined such that if the data is formatted properly and sent with a POST to the `/parallels/` endpoint, that data will be interpreted as the constraints for a Tesserae search and submit the query for processing.

The format for data accepted at the `/parallels/` endpoint is specified in the [`/parallels/` endpoint documentation](../endpoints/parallels.md).
The accepted format should (like the response data from the `/texts/` endpoint) be formatted in JSON, and the structure of the data will look as follows:
```json
{
  "source": ... ,
  "target": ... ,
  "method": ...
}
```
Note again the pattern of curly braces surrounding comma-separated entries, where each entry contains two parts separated by a colon (:).
The first part of the entry is surrounded by double quotes.
The second part is currently elided but will be revealed as we make further choices in how to constrain our Tesserae search.

### Specifying Texts and Units

Of course, an intertext necessitates a comparison between two texts.
Tesserae further requires specification of how to break up texts into passages or units.
An intertext, then, is an association between a unit from one text and a unit from another text.
We have already laid out the idea that one text will serve as the source text while the other is considered the target text, and by looking at the format that the `/parallels/` endpoint expects, we can see that there are `"source"` and `"target"` entries in the data.
By consulting [the details on units](../details/units.md), we see that we can specify text and unit options in JSON format, as follows:
```json
{
  "object_id": ... ,
  "units": ...
}
```

Acceptable options for `"units"` are `"line"` and `"phrase"`.
Since both the *Aeneid* and *Bellum Civile* are poems, we will choose the `"line"` option.
That means that both specifications will look something like this:
```json
{
  "object_id": ... ,
  "units": "line"
}
```

As for what option to use for `"object_id"`, that depends on the internal identifiers the TIS API uses to refer to the texts.
We can use the `/texts/` endpoint to query for our texts of interest, and the returned results (which are in JSON format) should contain an `"object_id"` entry.
For purposes of this tutorial, we will use placeholders to represent these internal identifiers.
If you want the command that will be revealed later in the tutorial to correctly submit a Tesserae search query, you will have to replace the placeholders with the actual identifiers you find through the `/texts/` endpoint.

So more concretely, suppose you use <https://tesserae.caset.buffalo.edu/api/texts/?author=vergil> to find information about the *Aeneid*.
You will find something like the following in the response:
```json
{
  "author": "vergil",
  "title": "aeneid",
  "object_id": <aeneid_id>,
  ...
}
```

Then, to specify the *Aeneid* as the source text for our search, we would include the text and unit information to the data we will submit to the `/parallels/` endpoint as follows:
```json
{
  "source": {
    "object_id": <aeneid_id>,
    "units": "lines"
  },
  "target": ... ,
  "method": ...
}
```

Assuming that `<bellum_id>` is the internal identifier of *Bellum Civile*, the submission data could be further filled out to:
```json
{
  "source": {
    "object_id": <aeneid_id>,
    "units": "lines"
  },
  "target": {
    "object_id": <bellum_id>,
    "units": "lines"
  },
  "method": ...
}
```

### Defining the `"method"` and Choosing Stopwords

Now that we have specified the source and target texts, we need to specify further options on how we would like Tesserae to search for intertexts between these two texts.
Details on the specifics can be found in the [scoring method details](../details/methods.md).
For this tutorial, we would like to run the Tesserae search with the following options (associated parameter names are in parentheses):

  * search by lemma (`"feature"`)
  * specify lemmata that shouldn't count as evidence for an intertext (`"stopwords"`)
  * use frequency statistics of only the *Aeneid* and *Bellum Civile* (`"freq_basis"`)
  * allow the distance between matching lemmata to be unconstrained (`"max_distance"`)
  * count distance based on lemma frequencies (`"distance_basis"`)

Filling out these options in the data we will be providing to the `/parallels/` endpoint brings that data to the following form:
```json
{
  "source": {
    "object_id": <aeneid_id>,
    "units": "lines"
  },
  "target": {
    "object_id": <bellum_id>,
    "units": "lines"
  },
  "method": {
    "name": "original",
    "feature": "lemmata",
    "stopwords": ... ,
    "score_basis": "lemmata",
    "freq_basis": "texts",
    "max_distance": 999,
    "distance_basis": "frequency"
  }
}
```

Note that although in reality, we have constrained maximum distance between matching lemmata to be 999, because no one line of the *Aeneid* nor *Bellum Civile* contains more than that number of words, it is as if the distance were unconstrained.

That leaves us with filling out stopwords, which are the lemmata we would like Tesserae to ignore when looking for evidence of intertexts.
Assuming that the most common words in a language are unhelpful in identifying intertexts, we might want to include the 10 most common lemmata in Latin as stopwords.
We can use the TIS API to query the 10 most common lemmata using the following URL:

  * <https://tesserae.caset.buffalo.edu/api/stopwords/?feature=lemmata&language=latin&list_size=10>

(Pop quiz:  How might <https://tesserae.caset.buffalo.edu/api/stopwords/?feature=lemmata&language=latin&list_size=50> be different?)

Filling in the stopwords with the results we obtained, we have the following (or something like it):
```json
{
  "source": {
    "object_id": <aeneid_id>,
    "units": "lines"
  },
  "target": {
    "object_id": <bellum_id>,
    "units": "lines"
  },
  "method": {
    "name": "original",
    "feature": "lemmata",
    "stopwords": [
      "qui", "quis", "sum", "et", "in",
      "is", "non", "hic", "ego", "ut"
    ],
    "score_basis": "lemmata",
    "freq_basis": "texts",
    "max_distance": 999,
    "distance_basis": "frequency"
  }
}
```

### Submitting the Query

Finally, we are ready to submit the query to the `/parallels/` endpoint.
Recall that we cannot submit a query by using GET on `/parallels/` because that is how the TIS API is defined.
Instead, we must use a POST on `/parallels/` and provide the data we built up above.
To do this, we will use the `curl` command.

This is the point where you will need a Unix terminal with `curl` installed.
(If you do not have `curl` installed on your system, a quick web search with "install curl" and your operating system should yield webpages with helpful instructions.)
Once you've installed `curl` and have your terminal open, you can submit the query with the following command (after you've substituted `<aeneid_id>` and `<bellum_id>`):
```bash
curl -i -X POST -H "Content-Type: application/json; charset=utf-8" \
"https://tesserae.caset.buffalo.edu/api/parallels/" \
--data-binary @- << EOF
{
  "source": {
    "object_id": <aeneid_id>,
    "units": "line"
  },
  "target": {
    "object_id": <bellum_id>,
    "units": "line"
  },
  "method": {
    "name": "original",
    "feature": "lemmata",
    "stopwords": [
      "qui", "quis", "sum", "et", "in",
      "is", "non", "hic", "ego", "ut"
    ],
    "score_basis": "lemmata",
    "freq_basis": "corpus",
    "max_distance": 999,
    "distance_basis": "frequency"
  }
}
EOF
```
If you blindly copied-and-pasted the above into your terminal, you'll probably have trouble fixing the parts that need to be substituted.
You may want to copy-and-paste the above into your favorite text editor, make the required substitutions, and then copy-and-paste from your text editor to the command line.

If everything is working correctly, you should see one of two things.
One possibility is that this search has already been run and saved temporarily.
In other words, the search has been cached.
In this case, the first line following the command should contain "303", which indicates that the results to the query are already available.
The other possibility is that the results to a search with this query has not been temporarily saved recently.
Thus, the full search must be run before results are made available.
In either case, the search results can be retrieved at the URL specified on the line that starts with "`Location: `".
If you request a GET at the URL (perhaps by entering the URL into your web browser) before search is complete, you will get a 404 (not found) error.
But if the search is complete, requesting GET at that URL will yield the results of the search.

## Final Thoughts

You've made it to the end of our tutorials!
You should now be equipped with enough knowledge to navigate the rest of the documentation.
For a slightly different presentation of the ideas presented in this advanced tutorial, you can look at the [example workflow](workflow.md).

If you're curious about how to know whether a search is complete, you may find [this endpoint](../endpoints/parallels-uuid-status.md) helpful.
