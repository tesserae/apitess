## Tesserae Intertext Service (TIS) API

This is the code used to implement the TIS API.  It is a flask application.

### Documentation Site

The API documentation is also stored in this repository under the `mkdocs-site`
directory.  It uses the `mkdocs` Python module to build the documentation.

At a high level, `mkdocs.yml` defines the overall organization of the
documentation site.  Anything in `docs` can be made available to the site.  The
pages are written in Markdown.  For more information on how to edit the files
in the `mkdocs-site` directory in order to make particular changes to the
documentation, see https://www.mkdocs.org/.

In order to build the mkdocs site, you will need to install `mkdocs` and
`python-markdown-math` via pip.

### Development

To run a development server to serve this flask application, you can use the
following command:
```
FLASK_APP=example/example_launcher.py FLASK_ENV=development python3 -m flask run
```

#### Running tests

To run the unit tests that come with this code, run:
```
ADMIN_INSTANCE=true python3 -m pytest
```
This will run the tests as if the flask application were being run as an
administrator instance, which allows adding, updating, and deleting of texts
and text metadata.
