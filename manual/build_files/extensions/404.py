# -*- encoding: utf-8 -*-
#
# Versioning for the 404 page.
# When you want to build an archive version update the versions.json file beforehand.
#

import os

from sphinx.util import logging


def html_page_context(app, pagename, templatename, context, doctree):
    """Adds a version tag variable to the context which can be accessed by the template."""

    if templatename == "404.html":
        gen_htaccess(app)


def gen_htaccess(app):
    text = read_htaccess()
    if text:
        try:
            build_dir = app.outdir
        except AttributeError as err:
            logger = logging.getLogger(__name__)
            logger.warning("404.py: Sphinx API change: {1}".format(err))
        else:
            write_htaccess(build_dir, text)


def read_htaccess():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    ht_fn = os.path.normpath(os.path.join(current_dir, "..", ".htaccess"))

    try:
        with open(ht_fn, "r", encoding="utf-8") as f:
            text = f.read()

    except (IOError, OSError) as err:
        logger = logging.getLogger(__name__)
        logger.warning("{0}: cannot read: {1}".format(ht_fn, err))
        return None
    else:
        return text


def write_htaccess(build_dir, text):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    ht_fn = os.path.normpath(os.path.join(current_dir, "..", build_dir, ".htaccess"))

    try:
        with open(ht_fn, "w", encoding="utf-8") as f:
            f.write(text)

    except (IOError, OSError) as err:
        logger = logging.getLogger(__name__)
        logger.warning("{0}: cannot write: {1}".format(ht_fn, err))
        return None


def setup(app):
    app.connect('html-page-context', html_page_context)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }