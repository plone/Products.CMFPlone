from ZPublisher.mapply import mapply
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
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
from FactoryTool import PendingCreate

debug = 0  # enable/disable logging

class NavigationTool (UniqueObject, SimpleItem):
    """ provides navigation related utilities """
    id = 'portal_navigation'
    meta_type= 'CMF Navigation Tool'
    security = ClassSecurityInfo()
    plone_tool = 1


    security.declarePublic('getNext')
    def getNext(self, context, script, status, **kwargs):
        """ Perform the next action specified by in portal_properties.navigation_properties.

            context - the current context

            script - the script/template currently being called

            status - 'success' or 'failure' strings used in calculating destination

            kwargs - additional keyword arguments are passed to subsequent pages either in
                the REQUEST or as GET parameters if a redirection needs to be done
        """
        (transition_type, transition) = self.getNavigationTransistion(context, script, status)
        self.log("%s.%s.%s(%s) -> %s:%s" % (context, script, status, str(kwargs), transition_type, transition), 'getNext')
        if transition_type == 'action':
            return self._dispatchAction(context, transition, **kwargs)
        elif transition_type == 'url':
            return self._dispatchUrl(context, transition, **kwargs)
        elif transition_type == 'script':
            return self._dispatchScript(context, transition, **kwargs)
        else:
            return self._dispatchPage(context, transition, **kwargs)


    def addTransitionFor(self, content, script, status, destination):
        """ Adds a transition.  When SCRIPT with context CONTENT returns STATUS, go to DESTINATION

            content - is a object or a TypeInfo that you would like to register.
                      A None content object will register Default values.

            script - the script/template that was just called

            status - SUCCESS or FAILURE strings used in calculating destination

            destination - is an action registed on the TypeInfo or a free-form script
                          that would be appended to the url of the content

            Destinations are specified as follows:
                action:ACTION_NAME invokes the action ACTION_NAME on the current context
                script:SCRIPT_NAME invokes the python script SCRIPT_NAME on the current context.
                        The script should return a tuple containing a status code (either 'success'
                        or 'failure') and optional kwargs.
                        getNext() will be called using the return code to determine the next page
                        to load.
                url:URL redirects to the url specified by URL
                PAGE invokes the page PAGE on the current context
        """

        property_tool = getattr(self, 'portal_properties')
        navprops = getattr(property_tool, 'navigation_properties') #propertymanager that holds data

        content=self._getContentFrom(content)
        status = self._normalize(status)
        script = self._normalize(script)

        if status not in self._availableStatus():
            raise KeyError, '%s status is not supported' % status

        transition = '%s.%s.%s'%( content
                                , script
                                , status )

        if navprops.hasProperty(transition):
            navprops._updateProperty(transition, destination)
        else:
            navprops._setProperty(transition, destination)


    security.declarePrivate('removeTransitionFor')
    def removeTransitionFrom(self, content, script=None, status=None):
        """ removes everything regarding a content/script combination """
        property_tool = getattr(self, 'portal_properties')
        navprops = getattr(property_tool, 'navigation_properties') #propertymanager that holds data
        transition = self._getContentFrom(content)
        script = self._normalize(script)
        status = self._normalize(status)
        if script is not None:
            transition += '.'+script
        if status is not None:
            transition += '.'+status
        for prop in navprops.propertyIds():
            if prop.startswith(transition):
                navprops._delProperty(prop)


    def _getContentFrom(self, content):
        """ returns the internal representation of content type """
        if content is None:
            content = 'Default'
        if hasattr(content, '__class__') and content.__class__ == PendingCreate:
            content = content.getPendingCreateType()
        if hasattr(content, 'getTypeInfo'):
#        if hasattr(content, '_isPortalContent'): #XXX Contentish xface
            content = content.getTypeInfo()
        if hasattr(content, 'getId'): #XXX use a xface
#        if hasattr(content, '_isTypeInformation'): #XXX use a xface
            content = content.getId()
        content = self._normalize(content) #normalize
        return content


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

    def _parseTransition(self, transition):
        type_list = ['action', 'url', 'script']

        for t in type_list:
            if transition.startswith(t+':'):
                return (t, transition[len(t)+1:].strip())
        return (None, transition.strip())

    def getNavigationTransistion(self, context, script, status):
        script = self._normalize(script) # normalize
        status = self._normalize(status) # normalize
        
        property_tool = getattr(self, 'portal_properties')
        navprops = getattr(property_tool, 'navigation_properties')

        transition_key = self._getContentFrom(context)+'.'+script+'.'+status
        transition = getattr(navprops.aq_explicit, transition_key, None)
        
        if transition is None:
            transition_key='%s.%s.%s' % (self._getContentFrom(None),script,status)
            transition = getattr(navprops.aq_explicit, transition_key, None)

            if transition is None:
                transition_key='%s.%s.%s' % (self._getContentFrom(None),'default',status)
                transition = getattr(navprops.aq_explicit, transition_key, None)

                if transition is None:
                    raise "Unable to find navigation transition for %s.%s.%s" % (self._getContentFrom(context), script, status)

        self.log("getting transition %s.%s.%s, found [%s]\n" % (context, script, status, str(transition)))
        
        transition = self._transitionSubstitute(transition, self.REQUEST)
        return self._parseTransition(transition)

    def _dispatchPage(self, context, page, **kwargs):
        # If any query parameters have been specified in the transition,
        # stick them into the request before calling getActionById()
        queryIndex = page.find('?')
        if queryIndex > -1:
            query = parse_qs(page[queryIndex+1:])
            for key in query.keys():
                if len(query[key]) == 1:
                    self.REQUEST[key] = query[key][0]
                else:
                    self.REQUEST[key] = query[key]
            page = page[0:queryIndex]

        self.log("page = " + str(page) + ", context = " + str(context), '_dispatchPage')
        if page is not None:
            return apply(context.restrictedTraverse(page), (context, context.REQUEST), kwargs)
        raise Exception, 'Argh! could not find the transition, ' + page

    def _dispatchScript(self, context, script, **kwargs):
        self.log('calling ' + script, '_dispatchScript')

        request = {}
        for key in self.REQUEST.keys():
            request[key] = self.REQUEST[key]
        request.update(kwargs)

        script_object = getattr(context, script)

        status = mapply(script_object, self.REQUEST.args, request,
                        call_object, 1, missing_name, dont_publish_class,
                        self.REQUEST, bind=1)

        self.log('status = ' + str(status), '_dispatchScript')
        if type(status) == type(()):
            (status, kwargs) = status
        else:
            kwargs = {}
        return self.getNext(context, script, status, **kwargs)
    
    def _dispatchRedirect(self, context, url, **kwargs):
        url = self._addUrlArgs(url, kwargs)
        self.log('url = ' + str(url), '_dispatchRedirect')
        return self.REQUEST.RESPONSE.redirect(url)

    def _dispatchAction(self, context, action_id, **kwargs):
        next_action = context.getTypeInfo().getActionById(action_id)
        url = self._addUrlArgs(next_action, kwargs)
        self.log('url = ' + str(url), '_dispatchAction')
        return self.REQUEST.RESPONSE.redirect('%s/%s' % (context.absolute_url(), url))

    def _addUrlArgs(self, base, kwargs):
        url_params=urlencode(kwargs)
        if base.find('?') >= 0:
            separator = '&'
        else:
            separator = '?'
            if len(url_params) == 0:
                separator = ''
        return base+separator+url_params 


    def _normalize(self, st):
        if st is None:
            return None
        return st.lower().replace(' ', '')


    def _availableStatus(self):
        return ('success', 'failure')


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        if not loc:
            loc = 'NavigationTool'
        else:
            loc = 'NavigationTool.'+loc
        sys.stdout.write(loc+': '+str(msg)+'\n')


    # DEPRECATED -- FOR BACKWARDS COMPATIBILITY WITH PLONE 1.0 ALPHA 2 ONLY
    # USE GETNEXT() INSTEAD AND UPDATE THE NAVIGATION PROPERTIES FILE
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, script, status, **kwargs):
        """ given a object, action_id and status we can fetch the next action
            for this object 
        """
        (transition_type, action_id) = self.getNavigationTransistion(context,script,status)
        
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

    # DEPRECATED -- FOR BACKWARDS COMPATIBILITY WITH PLONE 1.0 ALPHA 2 ONLY
    # USE GETNEXT() INSTEAD AND UPDATE THE NAVIGATION PROPERTIES FILE
    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, script, status, **kwargs):
        """ takes object, script, and status and returns a RESPONSE redirect """
        (transition_type, action_id) = self.getNavigationTransistion(context,script,status) ###
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
              
InitializeClass(NavigationTool)
