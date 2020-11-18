moved from plone.theme
======================

``plone.theme`` is deprecated, code is now part of Products.CMFPlone (since 5.2).

This package lets you mark the request with a "layer" interface conditional
on the currently selected skin (theme) in the portal_skins tool.

Most Zope 3 "visual" directives, like <browser:page /> or <browser:viewlet />
accept a 'layer' attribute, which should point to an interface. Recall that a
view is a multi-adapter on (context, request). Most views are registered
so that the 'request' being adapted only needs to provide Interface. This
is equivalent to saying layer="*".

By applying a marker interface to the request, and registering a view or
viewlet with this interface as the adapted 'layer', we can override a more
general view, or make a viewlet that is only shown for a particular layer.

In the context of CMF and Plone, we'd like to tie the layer to the current
skin selection. We do that by name.

What you have to do
-------------------

First, you should create a marker interface:

    >>> from zope.interface import Interface
    >>> class IMyTheme(Interface):
    ...     """Marker interface for skins part of 'My Theme'
    ...     """

Then, register this as a theme layer in ZCML:

    <interface
      interface=".interfaces.IMyTheme"
      type="zope.publisher.interfaces.browser.IBrowserSkinType"
      name="My Theme"
      />

The title here must match the name of the theme/skin selection in
portal_skins.

How it works
------------

Behind the scenes, the <interface /> registration marks IMyTheme with the
"IInterface" IThemelayer, and registers IMyTheme as a utility named "My Theme"
and providing IBrowserSkinType.

We do something to this effect in tests/tests.zcml.

Let us define the "My Theme" skin selection:

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal_skins = getToolByName(layer['portal'], 'portal_skins')
    >>> default_skin = portal_skins.getDefaultSkin()
    >>> skin_path = portal_skins._getSelections()[default_skin]
    >>> portal_skins.addSkinSelection('My Theme', skin_path)

In tests/tests.zcml we have registered two version of a view called
@@layer-test-view. One, for the default skin layer, simply outputs "Default".
The other outputs "My Theme".

Before we turn on the skin, we will get the default view.

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(layer['app'])

    >>> browser.open(layer['portal'].absolute_url() + '/@@layer-test-view')
    >>> from __future__ import print_function
    >>> print(browser.contents)
    Default

However, if we turn the skin on, we should see the effects of the marker
interface being applied.

    >>> portal_skins.default_skin = 'My Theme'
    >>> import transaction
    >>> transaction.commit()

    >>> browser.open(layer['portal'].absolute_url() + '/@@layer-test-view')
    >>> print(browser.contents)
    My Theme

And if we switch back:

    >>> portal_skins.default_skin = 'Plone Default'
    >>> transaction.commit()

    >>> browser.open(layer['portal'].absolute_url() + '/@@layer-test-view')
    >>> print(browser.contents)
    Default
