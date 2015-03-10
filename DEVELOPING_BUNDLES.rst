Introduction
============

This document is meant to help core developers hack on plone
bundles.

It's a work in progress and right now, it'll cover scenarios
of working on Plone bundles.


Background
----------

Plone bundle resources are mostly located in the mockup package and Products.CMFPlone/static.

Dependency Plone JavaScript resources are defined in Products.CMFPlone/static/bower.json

Products.CMFPlone/static/bower.json and mockup/bower.json are very close to the same. If you
change a dependency version in mockup/bower.json you're going to have to update that version
in Products.CMFPlone/static/bower.json. The reason for this is `mockup` does not commit
its dependency packages to its repository while Products.CMFPlone does. The difference
is due to fact that CMFPlone allows you to develop TTW and mockup is meant to be a simple
bower installable package(and when bower installs, it'll install the dependency).


Updating bundle resources
-------------------------

If you are updating Plone JavaScript resource while in development mode on your Plone instance,
you'll need to compile those changes in order for Plone to be shipped with your changes in
production mode. The general process is...

1) make your updates to JavaScript(could be in mockup project)
2) compile bundle you made changes to::

    cd path/to/buildout
    ./bin/plone-compile-resources --bundle=bundle-name


The final step requires you have a clean Plone instance available to know how to
build the JavaScript dependencies. You can provide `--instance` parameter to
customize which plone instance is used to build the bundle.


Upgrading JavaScript library
----------------------------

If you need to update a dependent version, the general workflow is:

1) update Products.CMFPlone/static/bower.json
2) run bower in Products.CMFPlone/static::

    cd path/to/Products/CMFPlone/static
    path/to/bower install

3) then, finally, compile bundle::

    cd path/to/buildout
    ./bin/plone-compile-resources --bundle=bundle-name


