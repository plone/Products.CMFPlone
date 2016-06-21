Introduction
============

This document is meant to help core developers hack on plone bundles.

It's a work in progress and right now, it'll cover scenarios of working on Plone bundles.


Background
----------

Plone bundle resources are mostly located in the mockup package and Products.CMFPlone/static.

Dependency Plone JavaScript resources are defined in Products.CMFPlone/static/bower.json

Products.CMFPlone/static/bower.json and mockup/bower.json are very close to the same.
If you change a dependency version in mockup/bower.json you're going to have to update that version in Products.CMFPlone/static/bower.json.
The reason for this is `mockup` does not commit its dependency packages to its repository while Products.CMFPlone does.
The difference is due to fact that CMFPlone allows you to develop TTW and mockup is meant to be a simple bower installable package (and when bower installs, it'll install the dependency).


Updating bundle resources
-------------------------

If you are updating Plone JavaScript resource while in development mode on your Plone instance, you'll need to compile those changes in order for Plone to be shipped with your changes in production mode.
The general process is:

1) Make your updates to JavaScript (could be in mockup project)
2) Compile bundle you made changes to::

    cd path/to/buildout
    ./bin/plone-compile-resources --bundle=bundle-name

3) In the ``registry.xml`` file where the bundle is registered, update the bundles ``last_compilation`` date/time value.
  Otherwise there might still an old, cached version be delivered.

4) If you update one of the core bundles (e.g. ``plone`` or ``plone-logged-in``) don't forget to add an registry entry with updated ``last_compilation`` in ``plone.app.upgrade`` too.

The final step requires you to have a clean Plone instance available which knows how to build the JavaScript dependencies.
You can provide `--instance` parameter to customize which Plone instance is used to build the bundle.


Upgrading JavaScript library
----------------------------

If you need to update a dependent version, the general workflow is:

1) Update Products.CMFPlone/static/bower.json
2) Run bower in Products.CMFPlone/static::

    cd path/to/Products/CMFPlone/static
    path/to/bower install

3) Then, finally, compile the bundle::

    cd path/to/buildout
    ./bin/plone-compile-resources --bundle=bundle-name

To get it as clean as possible without any unnecessary files, follow a similar process like this::

1) Copy ``bower.json``, ``.bowerrc`` and ``.gitignore`` to a new temporary working directory, which is not already managed by git.
2) Update ``bower.json`` in there.
3) Run ``bower install`` in there.
4) Eventually update ``.gitignore`` to ignore any new files not needed to build other bundles.
5) Run ``git init .``
6) Run ``git add .``
7) Remove the ``components`` directory in the temporary working directory.
8) Run ``git checkout .`` to checkout the components directory again, but this time only those files which ``.gitignore`` didn't ignore.
9) Replace ``static/components`` directory from CMFPlone with the ``components`` directory from your temporary working directory.

