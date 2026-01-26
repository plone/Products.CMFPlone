from plone.app.contenttypes.interfaces import ILink
from zope.component import getMultiAdapter

def get_absolute_remote_url(item, request):
    """
    Return the absolute remote URL for a Link item using its link_redirect_view.
    """
    if not ILink.providedBy(item):
        return None
    view = getMultiAdapter((item, request), name="link_redirect_view")
    return view.absolute_target_url()
