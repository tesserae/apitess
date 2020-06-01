# Scoring Methods

This page details parameters for Tesserae's intertext scoring algorithm.

## Tesserae Original

The original Tesserae intertext scoring algorithm was described by Forstall et al.[^1]

[^1]: Forstall, Christopher, Neil Coffee, Thomas Buck, Katherine Roache, and Sarah Jacobson. "Modeling the Scholars: Detecting Intertextuality through Enhanced Word-level N-gram Matching." Digital Scholarship in the Humanities 30, no. 4 (2014): 503-515.  See Figure 1.

### Algorithmic Overview

#### Definitions

"Texts" refer to literary works.

"Units" are sections within a text.

"Features" (or more accurately, "linguistic features") are the types of linguistically significant pieces of information found within a text span.  For example, words are a feature.

"Tokens" are the individual instances of a given feature.  Consider the following text span

  * the red truck stopped at the red sign

Clearly, this span contains words as features.  The words "the" and "red" appear twice in the span.  The first "the" is a token distinct from the other "the" later in the span; so also for "red".

#### Find Parallels

The algorithm begins by finding pairs of source text and target text spans which share at least two tokens of the same feature.  These pairs are called parallels.  For example, using the word feature (enforcing exact word matching) on the following two spans

  * nomadic children play with wooden toys
  * wooden horses suggest playing children

the token "children" occurs in both the first and second spans, as does "wooden".  Additionally, assuming the use of word feature again, the following two spans would be considered a pair sharing at least two tokens that are the same:

  * boys hate to lose to other boys
  * there are five boys here and six boys there

because they both share two word instances of "boys".

#### Reference Frequencies

The algorithm then continues by referencing frequency information concerning the matching tokens.  Frequency can be defined in terms of either the text or the corpus.

When defined in terms of some text Y, the frequency of word X is equal to the total number of tokens of the word X appearing in the text Y, divided by the total number of tokens in text Y.  For example, suppose we have the following text:

```
a a a a b
b b c b b
a a a a a
b a b a a
a b b b a
```

Now suppose the second line of this text is used as a source.  Then the frequency of the third token of that line, "c", will be 1/25 (since there is only one token of the word "c", and there are 25 total tokens in the text).

When defined in terms of the corpus, the frequency of word X is equal to the total number of tokens of the word X appearing in the corpus, divided by the total number of tokens in the corpus.  The corpus is defined to consist of all texts in the Tesserae database with the same language.  Thus, the `"latin"` corpus is separate from the `"greek"` corpus.

#### Compute Score

Finally, the algorithm computes a score for each text span pair according to the following formula:

$$ln\left(\frac{\sum_{m \in M}{\frac{1}{f_{t}(m)}} + \sum_{m \in M}{\frac{1}{f_{s}(m)}}}{d_{t}+d_{s}}\right)$$

where

  * $ln$ is the natural logarithm function
  * $M$ is the set of token types that both the source and target spans in the pair
    * a token of a type in $M$ is called a "matching token"
  * $f_t(m)$ computes the frequency of the feature $m$ with respect to the target span's text
    * if frequency is computed by corpus, $f_s(m)$ is computed by corpus statistics
  * $f_s(m)$ is like $f_t(m)$, except that it is with respect to the source
  * $d_t$ is the distance between two matching tokens in the target span (note that because the two tokens are matching, they must both be in the set $M$)
    * the distance is calculated by subtraction of the position numbers; i.e., in the text span "a c c c a", the two a's are separated by 4 tokens, since the a's occupy the 1st and 5th positions
    * an equivalent definition of distance:  adjacent tokens have a distance of 1, tokens with an intervening token have a distance of 2, etc.
    * which two matching tokens are used for calculating distance is a parameter that can be chosen; for more details, see [Distance Basis](#distance-basis)
  * $d_s$ is like $d_t$, except that it is with respect to the source

(if you find the mathematical symbols too small, you can either use the zoom function on your browser or right click on the math, hover over "Math Settings", then over "Zoom Trigger", and click on "Click"; then click on the math (you can unzoom by clicking again).)

### Method Parameterization

The original Tesserae scoring algorithm can be specified for use at the `/parallels/` endpoint as a JSON object with the following keys:

|Key|Value|
|---|---|
|`"name"`|Set to `"original"`.|
|`"feature"`|A string representing the linguistic feature to use for matching and scoring.  For more details, see [Features](#features).|
|`"stopwords"`|A list of strings, where each string represents a feature that should be ignored during matching.  This is useful, for example, when you want to ignore common function words.|
|`"freq_basis"`|Either `"texts"` or `"corpus"`.  If set to `"texts"`, scoring will compute frequency of a given token based on the text in which it is found; if set to `"corpus"`, frequency of a given token will be computed from all texts available in the Tesserae database of the same language as the text in which the token is found.  For more explanation, refer to [Reference Frequences](#reference-frequencies).|
|`"max_distance"`|A positive integer marking the maximum distance separating matching tokens within a span.  In other words, $d_s + d_t$ (from the equation in [Compute Score](#compute-score)) must be less than the maximum distance specified in order for a given source and target span to count as a parallel.  Setting this to some large value (like 999 when comparing lines of poetry) effectively makes this parameter unrestrictive.|
|`"distance_basis"`|A string describing which matching tokens will be used to calculate distance.  For more details, see [Distance Basis](#distance-basis).|

### Features

As noted earlier, the original Tesserae algorithm considers two spans to match when they share at least two tokens of the specified (linguistic) feature.  The following table describes what values are available for use with the `"feature"` key in the JSON object parameterizing the original Tesserae scoring algorithm sent as the request data payload at the `/parallels/` endpoint:

|Feature|Description|
|---|---|
|`"lemmata"`|Match by dictionary headword.|
|`"form"`|Match by exact word.|

### Distance Basis

As noted earlier, the distance between tokens is important to how the score for a pair is calculated.  The following table describes the options for determining this distance:

|Distance Basis|Description|
|---|---|
|`"span"`|The two farthest apart matching tokens within the span are used; $d_t>0$ and $d_s>0$ in this case.|
|`"frequency"`|The two lowest frequency tokens within the span are used. $d_t>0$ and $d_s>0$ in this case.|
