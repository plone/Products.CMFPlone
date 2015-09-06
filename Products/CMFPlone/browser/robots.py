# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import getMultiAdapter


class Robots(BrowserView):
    """Returns a robots.txt.

    It is ediable ttw in /@@site-controlpanel or by setting a different
    using a registry.xml with a line such as:
    <record name="plone.robots_txt">
        <value>User-agent: *
    Disallow: /
        </value>
    </record>
    """

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name='plone_portal_state')
        portal_url = portal_state.portal_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        return settings.robots_txt.format(portal_url=portal_url)
