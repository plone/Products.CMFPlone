from zope.interface import Interface, Attribute

class ITools(Interface):
    """A view that gives access to common tools
    """
    
    portal_actions     = Attribute("The portal_actions tool")
    portal_catalog     = Attribute("The portal_catalog tool")
    portal_interface   = Attribute("The portal_interface tool")
    portal_membership  = Attribute("The portal_membership tool")
    portal_properties  = Attribute("The portal_properties tool")
    portal_syndication = Attribute("The portal_syndication tool")
    portal_url         = Attribute("The portal_url tool")
    portal_workflow    = Attribute("The portal_workflow tool")
    
    plone_utils        = Attribute("The plone_utils tool")
    
class IPortalState(Interface):
    """A view that gives access to the current state of the portal
    """
    
    portal              = Attribute("The portal object")
    portal_title        = Attribute("The title of the portal object")
    portal_url          = Attribute("The URL of the portal object")
    navigation_root_url = Attribute("The URL of the navigation root")
    
    default_language    = Attribute("The default language in the portal")
    language            = Attribute("The current language")
    is_rtl              = Attribute("Whether or not the portal is being viewed in an RTL language")
    
    member              = Attribute("The current authenticated member")
    anonymous           = Attribute("Whether or not the current member is Anonymous")

class IContextState(Interface):
    """A view that gives access to the state of the current context
    """
    
    current_page_url     = Attribute("The URL to the current page, including template")
                            
    object_url           = Attribute("The URL of the current object")
    object_title         = Attribute("The prettified title of the current object")
    workflow_state       = Attribute("The workflow state of the current object")
    
    parent               =Attribute("The direct parent of the current object")
    folder               = Attribute("The current canonical folder")
                            
    is_folderish         = Attribute("True if this is a folderish object, structural or not")
    is_structural_folder = Attribute("True if this is a structural folder")
    is_default_page      = Attribute("True if this is the default page of its folder")
    
    is_editable          = Attribute("Whether or not the current object is editable")
    is_locked            = Attribute("Whether or not the current object is locked")
                            
    actions              = Attribute("The filtered actions in the context")
    keyed_actions        = Attribute("A mapping of action categories to action ids to "
                                     "action information: mapping[cat][id] == actioninfo")