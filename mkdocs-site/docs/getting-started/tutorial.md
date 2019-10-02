# Tutorial

This page describes some basic concepts of web API's in general, using examples from Tesserae's API.  The only skill assumed here is the ability to use a web browser.

## HyperText Transfer Protocol:  How the Internet Works

TODO:  explain HTTP methods

## Percent Encoding

TODO:  explain URL encoding

## Filtering Query Results

You can provide URL query strings to filter the results.  For example, the HTTP GET request for the resource

```
https://tesserae.caset.buffalo.edu/texts/?author=Vergil
```

asks Tesserae for information on literary works in its database that have "Vergil" as an author.  Multiple query filters can be applied, as shown in the following example:

```
https://tesserae.caset.buffalo.edu/texts/?author=Vergil&title=Georgics
```

This URL asks Tesserae for information on literary works in its database that have both "Vergil" as an author and "Georgics" as the title.

TODO:  Fill out rest of tutorial
