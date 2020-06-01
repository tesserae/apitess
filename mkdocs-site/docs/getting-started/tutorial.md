# Tutorial

This page describes some basic concepts of web API's in general, using examples from the TIS API.  The only skill assumed here is the ability to use a web browser.

## HyperText Transfer Protocol:  How the Internet Works

Whenever we visit a website through a web browser, we are actually initiating a conversation between two computers:  the one we're using the web browser on, and the one that serves the website to us.  For those computers to understand each other, that conversation is governed by a set of rules (or a protocol).

For this discussion, our focus will be on the HyperText Transfer Protocol, or HTTP.  You've probably seen that acronym, for example, in a URL to a website.  Due to security concerns, most websites nowadays are moving toward a more secure version of HTTP, which is why you will often see "https://" at the beginning of many website URLs (including the one you used to visit this page).

According to the conventions of HTTP (which also apply to its more secure version), one computer acts as the client (i.e., the requester of information), and one computer acts as the server (i.e., the one that responds to the request).  Back to the example of visiting a website, the computer we used to pull up a webpage would be the client, and the computer that gave the webpage to our computer would be the server.

Now, the client has two choices to make within the rules of HTTP:  which server to talk to, and which action to ask the server to take.  The choice of which server to talk to is determined by the URL.  The action to ask the server to take is not as easy to find on the web browser.  However, simply visiting a website is probably the GET action.  There are are other actions that a client could ask the server to take, and all of these actions, including GET, are known as HTTP methods.

## GET Texts from the TIS API

The TIS API is built as a server that speaks according to the rules of HTTP.  Thus, you can use your web browser to ask the TIS API to GET certain information for you.  For example, if you wanted to see what texts the TIS API has available, you could use the following URL in your web browser to ask the TIS API to GET available texts:

  * <https://tess-new.caset.buffalo.edu/api/texts/>

When you do this, you will see a bunch of plain text with lots of curly braces, commas, quotation marks, and colons.  Unlike a server built to return webpages, the TIS API is built to return information that is more computer-friendly than human-friendly.  The format of the plain text is known as JSON, and it is easy for a computer to read the information contained in it.

If you look carefully at the plain text, you might begin to see a pattern.  Between each set of curly braces are quoted words before and after a colon, and each quoted-words:quoted-words pattern is separated by a comma.  One of the quoted words that appears often on the left-hand side of a colon is "author"; another is "title".  If you read the corresponding quoted words to the right of the colon, you might notice a pattern.  The information contained within each pair of curly braces is an entry for texts that the TIS API has.

## Filtering with GET

There are a bunch of texts the TIS API has reported when our web browser asked it to GET using the previous URL.  Perhaps we are interested in only a certain subset of texts that the TIS API has.  It would be nice if we could filter the results somehow.

The TIS API supports URL query strings on that URL to filter results.  To specify a query string, first tack on a question mark to the end of the URL, then we give it a word, follow it with an equals sign, and then give it another word.  For example,

  * <https://tess-new.caset.buffalo.edu/api/texts/?author=vergil>

asks the TIS API for information on texts that have "vergil" as an author.  Multiple query filters can be applied, by separating each query string with an ampersand (&), as shown in the following example:

  * <https://tess-new.caset.buffalo.edu/api/texts/?author=vergil&title=georgics>

This URL asks the TIS API for texts that have both "vergil" as an author and "georgics" as the title.

## Moving Forward

To become more familiar with the concepts introduced in this tutorial, you might want to play around with the query strings.  For example, how might you ask the TIS API to GET texts by Aristotle?

When you feel comfortable with the material presented here, you could continue to the [advanced tutorial](advanced-tutorial.md).  Or if you feel brave, you could continue your exploration of the `/texts/` endpoint by reading [its documentation](../endpoints/texts.md).
