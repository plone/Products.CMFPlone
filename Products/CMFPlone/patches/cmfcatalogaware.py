import inspect
from Acquisition import aq_base
from OFS.interfaces import IObjectWillBeMovedEvent
from Products.CMFCore.CMFCatalogAware import handleContentishEvent as orig
from Products.CMFCore.interfaces import ICatalogTool
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.component import queryUtility


def handleContentishEvent(ob, event):
    """ Event subscriber for (IContentish, IObjectEvent) events.
    """
    if IObjectAddedEvent.providedBy(event):
        ob.notifyWorkflowCreated()
        ob.indexObject()

    elif IObjectWillBeMovedEvent.providedBy(event):
        if event.oldParent is not None:
            catalog = queryUtility(ICatalogTool)
            uid = catalog._CatalogTool__url(ob)
            if uid.startswith("/") or not event.newParent:
                ob.unindexObject()

    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            catalog = queryUtility(ICatalogTool)
            uid = catalog._CatalogTool__url(ob)
            if uid.startswith("/"):
                # path-based catalog key.
                # the object was unindexed at the old path
                # and needs to be completely re-added
                ob.indexObject()
            else:
                # UID-based catalog key.
                # we can update only the indexes that are path-dependent
                ob.reindexObject(idxs=["path", "allowedRolesAndUsers", "id", "getId"])

    elif IObjectCopiedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'workflow_history'):
            del ob.workflow_history

    elif IObjectCreatedEvent.providedBy(event):
        if hasattr(aq_base(ob), 'addCreator'):
            ob.addCreator()


globals = orig.__globals__
source = inspect.getsource(handleContentishEvent)
exec(source, globals)
orig.func_code = globals["handleContentishEvent"].__code__
