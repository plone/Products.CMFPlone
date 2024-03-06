"""Hang on, this is funny.

The summary is: if you want to (partially) disable Classic UI,
you can set an environment variable DISABLE_CLASSIC_UI=true.
This is a temporary measure for Plone 6.1+.
In Plone 7, Classic UI would be disabled by default,
unless the plone.classicui package is available.

How does this work?

In meta.zcml, we check if this module can be imported.
If the import works, we register a zcml feature "disable-classic-ui".
If the import doesn't work, we do nothing, and all is normal.

In this module, we check for an environment variable DISABLE_CLASSIC_UI.
We check if this has been set, and has a "truthy" value.

If it is truthy, we do nothing.
Result: this module can be imported.

If it is not set, or not truthy, we raise an ImportError.
Result: this module can't be imported.
This is actually the expected default case in Plone 6.

Now we can use zcml:condition="not-have disable-classic-ui"
around zcml parts that load zcml that is only of interest for Classic UI.

Some potential targets:

* portlets
* viewlets
* plonetheme.barceloneta
* plone.staticresources

In the first tests with portlets, we can see that it can be tricky to get this right.

* We can avoid loading the zcml of plone.portlets, plone.app.portlets,
  and plone.portlet.static/collection in CMFPlone, but plone.portlet.static
  has autoinclude of its zcml turned on setup.py, and loading it fails.
  This is something to fix in plone.portlet.static.
* plone.app.event defines two own portlets, so it needs to use the same
  conditional loading of this part of its zcml.
* The rolemap.xml of CMFPlone wants to set roles for a permission
  "Portlets: Manage portlets" and this fails unless we load the
  permissions.zcml from plone.app.portlets anyway.
* In metadata.xml of the CMFPlone dependencies profile, we want to install
  the default profiles of plone.portlet.collection/static, which fails.
  A solution would be to integrate the portlets.xml from these two packages in our own.
* Note that it is fine that CMFPlone has a portlets.xml: if the plone.app.portlets
  zcml is not loaded, no import handler is defined that reads this.
* plone.app.contentmenu defines a Portlets menu, which leads to non-existing urls.
  The contentmenu is specific for Classic UI though, so we might want to avoid
  loading this as well.
* Obviously lots of tests will fail.
  Nicest would be to have an extra job on Jenkins or GitHub Actions that installs
  only Products.CMFPlone and its test dependencies, and disable Classic UI there,
  and run the tests.
* It might be easier to first "unify" the portlets:
  * Move the portlets from plone.portlet.collection/static and plone.app.event
    to plone.app.portlets.
  * Keep BBB imports in place, to avoid breaking existing portlets.
  * Be careful to not introduce circular imports.
  * Move portlets.xml from CMFPlone to plone.app.portlets in a new profile.
  * Move the portlet part of rolemap.xml to plone.app.portlets.
  * Make sure to install the new profile by default: we only want to change
    this in Plone 7.
* Perhaps disabling plone.app.layout.viewlets is an easier first target
  for disabling a part of Classic UI. :-)

"""
import os


if os.getenv("DISABLE_CLASSIC_UI", "").lower() not in ("true", "yes", "on", "1"):
    raise ImportError("Explicitly raised ImportError to disable Classic UI.")
