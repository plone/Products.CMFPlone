from plone.base.interfaces.controlpanel import ISiteSchema
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility


class Robots(BrowserView):
    """Returns a robots.txt.

    It is editable ttw in /@@site-controlpanel or by setting a different
    using a registry.xml with a line such as:
    <record name="plone.robots_txt">
        <value>User-agent: *
    Disallow: /
        </value>
    </record>
    """

    def __call__(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        portal_url = portal_state.portal_url()
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        return settings.robots_txt.format(portal_url=portal_url)
