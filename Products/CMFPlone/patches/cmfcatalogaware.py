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
from zope.component import ComponentLookupError


def handleContentishEvent(ob, event):
    """ Event subscriber for (IContentish, IObjectEvent) events.
    """
    if IObjectAddedEvent.providedBy(event):
        ob.notifyWorkflowCreated()
        ob.indexObject()

    elif IObjectWillBeMovedEvent.providedBy(event):
        # Move/Rename
        if event.oldParent is not None and event.newParent is not None:
            try:
                catalog = queryUtility(ICatalogTool)
            except ComponentLookupError:
                # Happens when renaming a Plone Site in the ZMI.
                # Then it is best to manually clear and rebuild
                # the catalog later anyway.
                # But for now do what would happen without our patch.
                ob.unindexObject()
            else:
                ob_path = '/'.join(ob.getPhysicalPath())
                rid = catalog._catalog.uids.get(ob_path)
                if rid is not None:
                    setattr(ob, '__rid', rid)
                else:
                    # This may happen if deferred indexing is active and an
                    # object is added and renamed/moved in the same transaction
                    # (e.g. moved in an IObjectAddedEvent handler)
                    return
        elif event.oldParent is not None:
            # Delete
            ob.unindexObject()

    elif IObjectMovedEvent.providedBy(event):
        if event.newParent is not None:
            rid = getattr(ob, '__rid', None)
            if rid:
                catalog = queryUtility(ICatalogTool)
                _catalog = catalog._catalog

                new_path = '/'.join(ob.getPhysicalPath())
                old_path = _catalog.paths[rid]

                del _catalog.uids[old_path]
                _catalog.uids[new_path] = rid
                _catalog.paths[rid] = new_path

                ob.reindexObject(
                    idxs=["allowedRolesAndUsers", "path", "getId", "id"]
                )

                delattr(ob, '__rid')
            else:
                # This may happen if deferred indexing is active and an
                # object is added and renamed/moved in the same transaction
                # (e.g. moved in an IObjectAddedEvent handler)
                ob.indexObject()

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
