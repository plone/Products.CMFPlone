from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from types import TupleType
from urllib import urlencode
from cgi import parse_qs
import re

class NavigationTool (UniqueObject, SimpleItem):
    """ provides navigation related utilities """
    id = 'portal_navigation'
    meta_type= 'CMF Navigation Tool'
    security = ClassSecurityInfo()
    plone_tool = 1

    # Transitions are determined by a set of actions listed in a properties file.
    # One can include information from the REQUEST into a transition by using 
    # an expression enclosed in brackets, i.e. something of the form [foo].
    # The bracketed expression will be replaced by REQUEST['foo'], or an empty
    # string if the REQUEST has no key 'foo'.  To specify an alternative action
    # in the event that the REQUEST has no key 'foo', use [foo|bar].  If REQUEST.foo
    # doesn't exist, then the bracketed expression is replaced by bar.
    #
    # Example: document.document_edit.success:string=view?came_from=[came_from|/]
    #
    # Regular expression used for performing substitutions in navigation transitions:
    # Find a [ that is not prefixed by a \, then
    # get everything until we hit a ] not prefixed by a \,
    # then get the terminal ]
    transitionSubExpr = r"""(?:(?<!\\)\[)(?P<expr>(?:[^\]]|(?:(?<=\\)\]))*)(?:(?<!\\)\])"""
    transitionSubReg = re.compile(transitionSubExpr, re.VERBOSE)

    def _transitionSubstitute(self, action, REQUEST):
        action2 = ''
        segments = self.transitionSubReg.split(action)
        count = 0
        for seg in segments:
            if count % 2:
                separatorIndex = seg.find('|')
                if separatorIndex >= 0:
                    key = seg[0:separatorIndex]
                    fallback = seg[separatorIndex+1:]
                else:
                    key = seg
                    fallback = ''
                action2 = action2 + REQUEST.get(key, fallback)
            else:
                action2 = action2 + seg
            count = count + 1
        action2 = action2.replace('\[', '[')
        action2 = action2.replace('\]', ']')
        return action2

    def getNavigationTransistion(self, context, action, status):
        navprops = getattr(self, 'navigation_properties')
        fixedTypeName = ''.join(context.getTypeInfo().getId().lower().split(' '))
        navTransition = fixedTypeName+'.'+action+'.'+status
        action_id = getattr(navprops.aq_explicit, navTransition, None)
        if action_id is None:
            navTransition='%s.%s.%s' % ('default',action,status)
            action_id = getattr(navprops.aq_explicit, navTransition, None)
        if action_id is None:
            navTransition='%s.%s.%s' % ('default','default',status)
            action_id = getattr(navprops.aq_explicit, navTransition, '')
        return self._transitionSubstitute(action_id, self.REQUEST)

    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, action, status, **kwargs):
        """ given a object, action_id and status we can fetch the next action
            for this object 
        """
        action_id=self.getNavigationTransistion(context,action,status)
        # If any query parameters have been specified in the transition,
        # stick them into the request before calling getActionById()
        queryIndex = action_id.find('?')
        if queryIndex > -1:
            query = parse_qs(action_id[queryIndex+1:])
            for key in query.keys():
                if len(query[key]) == 1:
                    self.REQUEST[key] = query[key][0]
                else:
                    self.REQUEST[key] = query[key]
            action_id = action_id[0:queryIndex]

        # destination in the navigation properties that are enclosed in "
        # are meant to be literal pagetemplate id that are valid
        next_action=''
        if action_id.find('"')==-1:
            next_action=context.getTypeInfo().getActionById(action_id)
        else:
            next_action=action_id[1:len(action_id)-1]
        if next_action is not None:
            return context.restrictedTraverse(next_action)
        raise Exception, 'Argh! could not find the transition, ' + navTransition
            
    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, action, status, **kwargs):
        """ takes object, action, and status and returns a RESPONSE redirect """
        action_id=self.getNavigationTransistion(context,action,status) ###
        if action_id.find('?') >= 0:
            separator = '&'
        else:
            separator = '?'
            
        url_params=urlencode(kwargs)
        redirect=None
        next_action=''
        
        if action_id.find('"')==-1:
            next_action=context.getTypeInfo().getActionById(action_id)
        else:
            next_action=action_id[1:len(action_id)-1]
            
        return self.REQUEST.RESPONSE.redirect( '%s/%s%s%s' % ( context.absolute_url()
                                                             , next_action
                                                             , separator
                                                             , url_params) )

    def _availableStatus(self):
        return ('success', 'failure')

    def getContentFrom(self, content):
        """ returns the internal representation of content type """
        if content is None:
            content = 'Default'
        if hasattr(content, '_isPortalContent'): #XXX Contentish xface
            content = content.getTypeInfo()
        if hasattr(content, '_isTypeInformation'): #XXX use a xface
            content = content.getId()
        content = ''.join(content.split(' ')).lower() #normalize
        return content

    def addTransitionFor(self, content, action, status, destination):
        """ adds a transition 

            content - is a object or a TypeInfo that you would like to
                      register a None content object will register Default values.

            action - script that is used by content edit form
                     XXX this kinda hokey and error prone

            status - SUCCESS or FAILURE strings used in calculating destination

            destination - is an action registed on the TypeInfo or a free-form script
                          that would be appended to the url of the content
        """

        navprops = getattr(self, 'navigation_properties') #propertymanager that holds data
        status = status.lower()
        action = action.lower()

        if status not in self._availableStatus():
            raise KeyError, '%s status is not supported' % status

        content=self.getContentFrom(content)

        transition = '%s.%s.%s'%( content
                                , action
                                , status )

        if navprops.hasProperty(transition):
            navprops._updateProperty(transition, destination)
        else:
            navprops._setProperty(transition, destination)

    security.declarePrivate('removeTransitionFor')
    def removeTransitionFrom(self, content, action=None, status=None):
        """ removes everything regarding a content/action combination """
        navprops = getattr(self, 'navigation_properties') #propertymanager that holds data
        transition = self.getContentFrom(content)
        if action is not None:
            transition += '.'+action
        if status is not None:
            transition += '.'+status
        for prop in navprops.propertyIds():
            if prop.startswith(transition):
                navprops._delProperty(prop)

            
InitializeClass(NavigationTool)
