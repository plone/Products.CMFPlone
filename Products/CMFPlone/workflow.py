from zope.interface import Interface, implementer
from zope.component import adapter
from Acquisition import aq_base
from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFPlone.interfaces import IWorkflowChain


@adapter(Interface, IWorkflowTool)
@implementer(IWorkflowChain)
def ToolWorkflowChain(context, workflow_tool):
    """Looks up the workflow chain by portal type suing a mapping
    stored on the tool::

      >>> from Products.CMFPlone.tests.dummy import DummyContent, DummyWorkflowTool
      >>> tool = DummyWorkflowTool()
      >>> content = DummyContent(id='dummy', portal_type='DummyType')

    Either an object with a portal_type or the portal_type as a
    string.  If we pass in an unknown portal_type we get the default
    chain::

      >>> ToolWorkflowChain('A Type', tool)
      ('Default Workflow',)
      >>> tool.setChainForPortalTypes(('A Type',), ('Some Workflow',))
      >>> ToolWorkflowChain('A Type', tool)
      ('Some Workflow',)

    When we pass in a piece of content we get similar behavior::

      >>> ToolWorkflowChain(content, tool)
      ('Default Workflow',)
      >>> tool.setChainForPortalTypes(('DummyType',), ('Some Workflow',))
      >>> ToolWorkflowChain(content, tool)
      ('Some Workflow',)

   If we can't figure out a portal_type then we return an empty chain::

      >>> ToolWorkflowChain((), tool)
      ()

    """
    if isinstance(context, basestring):
        pt = context
    elif hasattr(aq_base(context), 'getPortalTypeName'):
        pt = context.getPortalTypeName()
    else:
        pt = None
    if pt is None:
        return ()
    chain = None

    # Unfortunately we need to rely on a private variable here
    cbt = workflow_tool._chains_by_type

    if cbt is not None:
        chain = cbt.get(pt, None)
    if chain is None:
        chain = workflow_tool.getDefaultChainFor(context)
        if chain is None:
            return ()
    return chain
