from Products.Five import BrowserView
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.utils import unhashPortletInfo

from plone.app.portlets.interfaces import IDeferredPortletRenderer
from plone.app.portlets.utils import assignment_from_key


class PortletUtilities(BrowserView):

    def render_portlet(self, portlethash, **kw):
        # Prepare the portlet and render the data
        info = unhashPortletInfo(portlethash)
        manager = getUtility(IPortletManager, info['manager'])

        assignment = assignment_from_key(context=self.context,
                                         manager_name=info['manager'],
                                         category=info['category'],
                                         key=info['key'],
                                         name=info['name'])
        renderer = getMultiAdapter(
                (self.context, self.request, self,
                 manager, assignment.data),
                IPortletRenderer
            )
        renderer = renderer.__of__(self.context)

        renderer.update()
        if IDeferredPortletRenderer.providedBy(renderer):
            # if this is a deferred load, prepare now the data
            renderer.deferred_update()
        return renderer.render()
