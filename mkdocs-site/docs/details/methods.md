# Scoring Methods

This page details parameters for Tesserae's intertext scoring algorithm.

## Tesserae Original

The original Tesserae intertext scoring algorithm was described by Forstall et al.[^1]

[^1]: Forstall, Christopher, Neil Coffee, Thomas Buck, Katherine Roache, and Sarah Jacobson. "Modeling the Scholars: Detecting Intertextuality through Enhanced Word-level N-gram Matching." Digital Scholarship in the Humanities 30, no. 4 (2014): 503-515.  See Figure 1.

### Algorithmic Overview

#### Definitions

"Texts" refer to literary works.

"Units" are sections within a text.

"Tokens" are the individual instances of words found in a text.  Consider the following text span

  * the red truck stopped at the red sign

Clearly, this span contains words.  The words "the" and "red" appear twice in the span.  The first "the" is a token distinct from the other "the" later in the span; so also for "red".

"Features" (or more accurately, "linguistic features") are the types of linguistically significant pieces of information found within a token.  The feature may be as simple as the text of the token or more complicated, like the possible lemmata for the token.

"Score Basis" is a feature type based on which scores will be computed.

#### Find Parallels

The algorithm begins by finding paralells, which are pairs of source text and target text spans which have at least two matching tokens.  Tokens are considered to match across spans based on a common feature.  For example, using the form feature (enforcing exact word matching) on the following two spans

  * nomadic children play with wooden toys
  * wooden horses suggest playing children

the matching tokens are "children" and "wooden".  Note that the token "children" in the first text span contains the form feature "children", which is the same form feature of the token "children" in the second text span.  The "wooden" tokens share an analogous relationship.  Thus, "children" and "wooden" are the matching tokens of these two text spans.

Here is another example parallel based on the form feature:

  * boys hate to lose to other boys
  * there are five boys here and six boys there

Here, both text spans have two instances each of the "boys" token.

#### Reference Frequencies

The algorithm then continues by referencing frequency information concerning the matching tokens.  Frequency can be defined in terms of two dimensions. One dimension is the population from which to draw these frequencies: either the text or the corpus. The other dimension is the score basis, or which feature to use when calculating a frequency score for a token.

When defined in terms of some text Y, the frequency of token X with respect to its form is equal to the total number of X tokens appearing in the text Y, divided by the total number of tokens in text Y.  For example, suppose we have the following text:

```
a a a a b
b b c b b
a a a a a
b a b a a
a b b b a
```

Now suppose the second line of this text is used as a source.  Then the frequency of the third token of that line, "c", will be 1/25 (since there is only one token of the word "c", and there are 25 total tokens in the text).

When defined in terms of the corpus, the frequency of a token X with respect to its forms is equal to the total number of X tokens appearing in the corpus, divided by the total number of tokens in the corpus.  The corpus is defined to consist of all texts in the Tesserae database with the same language.  Thus, the `"latin"` corpus is separate from the `"greek"` corpus.

When calculating frequencies for tokens with respect to other features where
more than one feature instance might be present in a given token, the frequency
is calculated in the following way. Let X by the token of interest, and the set
A contain the feature instances present in X.

To compute a text-based frequency, count up the number of tokens in the text
that share at least one feature in A. Divide that count by the total number of
tokens in the text. This is the text-based frequency of token X with respect to
the feature type of the elements of A.

To compute a corpus-based frequency, count up the number of times a feature
instance in A is found in the tokens of the corpus and divide that count by the
total number of feature instances extracted from the corpus. For example,
suppose that every token in the corpus had exactly two feature instances. Then
the total number of feature instances extracted from the corpus is twice the
total number of tokens in the corpus. Returning back to the other feature
instances in A, calculate analogous values. Now, take the average of these
values. This will be the corpus-based frequency of token X with respect to the
feature type of the elements of A.

#### Compute Score

Finally, the algorithm computes a score for each text span pair according to the following formula:

$$ln\left(\frac{\sum_{m \in M}{\frac{1}{f_{t}(m)}} + \sum_{m \in M}{\frac{1}{f_{s}(m)}}}{d_{t}+d_{s}}\right)$$

where

  * $ln$ is the natural logarithm function
  * $M$ is the collection of matching tokens of the pair
  * $f_t(m)$ is the target-based frequency of the matching token $m$ with respect to the score basis, if frequencies are to be text-based; otherwise, the frequencies are corpus-based
  * $f_s(m)$ is like $f_t(m)$, except that it is source-based in the case that
    frequencies are to be text-based
  * $d_t$ is the distance between two matching tokens in the target span (note that because the two tokens are matching, they must both be in the set $M$)
    * the distance is calculated by the number of tokens in the shortest subspan that contains both tokens; i.e., in the text span "a b b b c", the distance, assuming that "a" and "c" are the matching tokens, is 5
    * an equivalent definition of distance:  adjacent tokens have a distance of 2, tokens with an intervening token have a distance of 3, etc.
    * which two matching tokens are used for calculating distance is a parameter that can be chosen; for more details, see [Distance Basis](#distance-basis)
  * $d_s$ is like $d_t$, except that it is with respect to the source

(if you find the mathematical symbols too small, you can either use the zoom function on your browser or right click on the math, hover over "Math Settings", then over "Zoom Trigger", and click on "Click"; then click on the math (you can unzoom by clicking again).)

### Method Parameterization

The original Tesserae scoring algorithm can be specified for use at the `/parallels/` endpoint as a JSON object with the following keys:

|Key|Value|
|---|---|
|`"name"`|Set to `"original"`.|
|`"feature"`|A string representing the linguistic feature to use for matching.  For more details, see [Features](#features).|
|`"stopwords"`|A list of strings, where each string represents a feature that should be ignored during matching.  This is useful, for example, when you want to ignore common function words.|
|`"score_basis"`|A string representing the linguistic feature to use for scoring. For more details, see [Features](#features).|
|`"freq_basis"`|Either `"texts"` or `"corpus"`.  If set to `"texts"`, scoring will compute frequency of a given token based on the text in which it is found; if set to `"corpus"`, frequency of a given token will be computed from all texts available in the Tesserae database of the same language as the text in which the token is found.  For more explanation, refer to [Reference Frequencies](#reference-frequencies).|
|`"max_distance"`|A positive integer marking the maximum distance separating matching tokens within a span.  In other words, $d_s + d_t$ (from the equation in [Compute Score](#compute-score)) must be less than the maximum distance specified in order for a given source and target span to count as a parallel.  Setting this to some large value (like 999 when comparing lines of poetry) effectively makes this parameter unrestrictive.|
|`"distance_basis"`|A string describing which matching tokens will be used to calculate distance.  For more details, see [Distance Basis](#distance-basis).|
|`"min_score"`|A floating point value indicating a minimum score a match must have in order to be kept and reported. This is an optional value, and its default value is 0.|

### Features

As noted earlier, the original Tesserae algorithm considers two spans to match when they share at least two tokens of the specified (linguistic) feature.  It is also the case that the frequencies used in calculating the score of a match can also be computed with respect to the same or different specified feature. The following table describes what values are available for use with the `"feature"` and `"score_basis"` keys in the JSON object parameterizing the original Tesserae scoring algorithm sent as the request data payload at the `/parallels/` endpoint:

|Feature|Description|
|---|---|
|`"form"`|Match/score by exact word.|
|`"lemmata"`|Match/score by dictionary headword.|
|`"semantic"`|Match/score by synonyms.|
|`"semantic + lemmata"`|Match/score by synonyms and lemmata.|
|`"sound"`|Match/score by character trigrams.|

### Distance Basis

As noted earlier, the distance between tokens is important to how the score for a pair is calculated.  The following table describes the options for determining this distance:

|Distance Basis|Description|
|---|---|
|`"span"`|The two farthest apart matching tokens within the span are used; $d_t>0$ and $d_s>0$ in this case.|
|`"frequency"`|The two lowest frequency tokens within the span are used. $d_t>0$ and $d_s>0$ in this case.|

## Greek to Latin

It is possible to adapt the original Tesserae search to perform cross-language
search. A Greek to Latin search has been developed and can be used at the
`/parallels/` endpoint. Take care to specify the Greek work as the source text
and a Latin work as the target text when using this method.

### Method Parameterization

The Greek to Latin Tesserae scoring algorithm can be specified for use at the `/parallels/` endpoint as a JSON object with the following keys:

|Key|Value|
|---|---|
|`"name"`|Set to `"greek_to_latin"`.|
|`"greek_stopwords"`|A list of strings, where each string represents a Greek lemma that should be ignored during matching.  This is useful, for example, when you want to ignore common function words.|
|`"latin_stopwords"`|A list of strings, where each string represents a Latin lemma that should be ignored during matching.  This is useful, for example, when you want to ignore common function words.|
|`"freq_basis"`|Either `"texts"` or `"corpus"`.  If set to `"texts"`, scoring will compute frequency of a given token based on the text in which it is found; if set to `"corpus"`, frequency of a given token will be computed from all texts available in the Tesserae database of the same language as the text in which the token is found.  For more explanation, refer to [Reference Frequencies](#reference-frequencies).|
|`"max_distance"`|A positive integer marking the maximum distance separating matching tokens within a span.  In other words, $d_s + d_t$ (from the equation in [Compute Score](#compute-score)) must be less than the maximum distance specified in order for a given source and target span to count as a parallel.  Setting this to some large value (like 999 when comparing lines of poetry) effectively makes this parameter unrestrictive.|
|`"distance_basis"`|A string describing which matching tokens will be used to calculate distance.  For more details, see [Distance Basis](#distance-basis).|
|`"min_score"`|A floating point value indicating a minimum score a match must have in order to be kept and reported. This is an optional value, and its default value is 0.|
