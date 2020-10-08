from Acquisition import aq_base
from Acquisition import aq_parent
from Acquisition import aq_inner
from plone.registry.interfaces import IRegistry
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFDynamicViewFTI.interfaces import IDynamicViewTypeInformation
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.component import queryMultiAdapter


def get_default_page(context):
    """Given a folderish item, find out if it has a default-page using
    the following lookup rules:

        1. A content object called 'index_html' wins
        2. Else check for IBrowserDefault, either if the container implements
           it or if an adapter exists. In both cases fetch its FTI and either
           take it if it implements IDynamicViewTypeInformation or adapt it to
           IDynamicViewTypeInformation. call getDefaultPage on the implementer
           and take value if given.
        3. Else, look up the attribute default_page on the object, without
           acquisition in place
        3.1 look for a content in the container with the id, no acquisition!
        3.2 look for a content at portal, with acquisition
        4. Else, look up the property default_page in site_properties for
           magic ids and test these

    The id of the first matching item is then used to lookup a translation
    and if found, its id is returned. If no default page is set, None is
    returned. If a non-folderish item is passed in, return None always.
    """
    # met precondition?
    if not IFolderish.providedBy(context):
        return

    # The ids where we look for default - must support __contains__
    ids = set()

    # For BTreeFolders we just use the __contains__ otherwise build a set
    if isinstance(aq_base(context), BTreeFolder2Base):
        ids = context
    elif hasattr(aq_base(context), 'objectIds'):
        ids = set(context.objectIds())

    # 1. test for contentish index_html
    if 'index_html' in ids:
        return 'index_html'

    # 2. Test for IBrowserDefault
    if IBrowserDefault.providedBy(context):
        browserDefault = context
    else:
        browserDefault = queryAdapter(context, IBrowserDefault)

    if browserDefault is not None:
        fti = context.getTypeInfo()
        if fti is not None:
            if IDynamicViewTypeInformation.providedBy(fti):
                dynamic_fti = fti
            else:
                dynamic_fti = queryAdapter(fti, IDynamicViewTypeInformation)
            if dynamic_fti is not None:
                page = dynamic_fti.getDefaultPage(context, check_exists=True)
                if page is not None:
                    return page

    # 3.1 Test for default_page attribute in folder, no acquisition
    pages = getattr(aq_base(context), 'default_page', [])
    if isinstance(pages, str):
        pages = [pages]
    for page in pages:
        if page and page in ids:
            return page

    portal = queryUtility(ISiteRoot)
    # Might happen during portal creation
    if portal is None:
        return

    # 3.2 Test for default page in portal, acquire
    for page in pages:
        if portal.unrestrictedTraverse(page, None):
            return page

    # 4. Test for default sitewide default_page setting
    registry = getUtility(IRegistry)
    for page in registry.get('plone.default_page', []):
        if page in ids:
            return page


def is_default_page(container, obj):
    """Finds out if the given obj is the default page in its parent folder.

    Only considers explicitly contained objects, either set as index_html,
    with the default_page property, or using IBrowserDefault.
    """
    parent_default_page = get_default_page(container)
    precondition = (
        parent_default_page is not None
        and '/' not in parent_default_page
        and hasattr(aq_base(obj), 'getId')
    )
    return precondition and (parent_default_page == obj.getId())


def _getDefaultPageView(obj, request):
    """This is a nasty hack because the view lookup fails when it occurs too
       early in the publishing process because the request isn't marked with
       the default skin.  Explicitly marking the request appears to cause
       connection errors, so we just instantiate the view manually.
    """
    view = queryMultiAdapter((obj, request), name='default_page')
    if view is None:
        # mask circular import
        from Products.CMFPlone.browser.defaultpage import DefaultPage
        view = DefaultPage(obj, request)
    return view


def check_default_page_via_view(obj, request):
    container = aq_parent(aq_inner(obj))
    if container is None:
        return False
    view = _getDefaultPageView(container, request)
    return view.isDefaultPage(obj)


def get_default_page_via_view(obj, request):
    # Short circuit if we are not looking at a Folder
    if not obj.isPrincipiaFolderish:
        return None
    view = _getDefaultPageView(obj, request)
    return view.getDefaultPage()
