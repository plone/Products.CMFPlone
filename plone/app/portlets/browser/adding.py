from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter

from zope.container.interfaces import INameChooser

from Acquisition import aq_inner, aq_base, aq_parent
from OFS.SimpleItem import SimpleItem
from Products.Five import BrowserView

from plone.app.portlets.browser.interfaces import IPortletAdding
from plone.app.portlets.interfaces import IPortletPermissionChecker


class PortletAdding(SimpleItem, BrowserView):
    implements(IPortletAdding)

    context = None
    request = None

    # This is necessary so that context.absolute_url() works properly on the
    # add form, which in turn fixes the <base /> URL
    id = '+'

    def add(self, content):
        """Add the rule to the context
        """
        context = aq_inner(self.context)
        manager = aq_base(context)

        IPortletPermissionChecker(context)()

        chooser = INameChooser(manager)
        manager[chooser.chooseName(None, content)] = content

    def nextURL(self):
        referer = self.request.get('referer')
        if not referer:
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            referer = url + '/@@manage-portlets'
        return referer

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False

    @property
    def contentName(self):
        return None

    def addingInfo():
        return None

    def isSingleMenuItem():
        return False

    def hasCustomAddView():
        return 0
