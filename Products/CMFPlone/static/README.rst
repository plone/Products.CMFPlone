Introduction
============

We download some of Plone's dependent JavaScript modules here into
the components directory.

If you change bower.json, you'll need to run `bower install` on this
directory to update components with the changes.


Warning
-------

If you update r.js or less, you'll need to manually re-apply a patch
that gets us cache busting resource downloads so we can build
TTW.

See https://github.com/plone/Products.CMFPlone/commit/2d3865805efc6b72dce236eb68e502d8c57717b6
and https://github.com/plone/Products.CMFPlone/commit/bd1f9ba99d1ad40bb7fe1c00eaa32b8884aae5e2