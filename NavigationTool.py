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
from PloneUtilities import log as debug_log
from PloneUtilities import log_deprecated
from urlparse import urlparse, urljoin
import re
import traceback
import sys

from interfaces.NavigationController import INavigationController

debug = 0  # enable/disable logging

class NavigationTool (UniqueObject, SimpleItem):
    """ provides navigation related utilities """
    id = 'portal_navigation'
    meta_type= 'CMF Navigation Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    __implements__ = INavigationController,

    security.declarePublic('getNext')
    def getNext(self, context, script, status, trace=['\n'], **kwargs):
        """ Perform the next action specified by in portal_properties.navigation_properties.

            context - the current context

            script - the script/template currently being called

            status - 'success' or 'failure' strings used in calculating destination

            kwargs - additional keyword arguments are passed to subsequent pages either in
                the REQUEST or as GET parameters if a redirection needs to be done

            trace - navigation trace for internal use
        """
        try:
            trace.append('Looking up transition for %s.%s.%s' % (context, script, status))
            (transition_type, transition) = self.getNavigationTransition(context, script, status)
            trace.append('Found transition: %s, %s' % (transition_type, transition))
#            self.log("%s.%s.%s(%s) -> %s:%s" % (context, script, status, str(kwargs), transition_type, transition), 'getNext')

            if transition_type == 'action':
                return self._dispatchAction(context, transition, trace, **kwargs)
            elif transition_type == 'url':
                return self._dispatchUrl(context, transition, trace, **kwargs)
            elif transition_type == 'script':
                return self._dispatchScript(context, transition, trace, **kwargs)
            else:
                return self._dispatchPage(context, transition, trace, **kwargs)
        except NavigationError:
            raise
        except Exception, e:
             raise NavigationError(e, trace)


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
                url:URL redirects to the url specified by URL.  URL may be absolute or relative
                PAGE invokes the page PAGE on the current context
        """

        property_tool = getattr(self, 'portal_properties')
        navprops = getattr(property_tool, 'navigation_properties') #propertymanager that holds data

        content=self._getContentFrom(content)
        status = self._normalize(status, lower=1)
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
        if hasattr(content, 'getTypeInfo'):
#        if hasattr(content, '_isPortalContent'): #XXX Contentish xface
            content = content.getTypeInfo()
        if hasattr(content, 'getId'): #XXX use a xface
#        if hasattr(content, '_isTypeInformation'): #XXX use a xface
            content = content.getId()
        content = self._normalize(content, lower=1) #normalize
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


    def getNavigationTransition(self, context, script, status):
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
                    raise KeyError, "Unable to find navigation transition for %s.%s.%s" % (self._getContentFrom(context), script, status)

#        self.log("getting transition %s.%s.%s, found [%s]\n" % (context, script, status, str(transition)))
        
        transition = self._transitionSubstitute(transition, self.REQUEST)
        return self._parseTransition(transition)


    def _dispatchPage(self, context, page, trace, **kwargs):
        # If any query parameters have been specified in the transition,
        # stick them into the request before calling getActionById()
        try:
            queryIndex = page.find('?')
            if queryIndex > -1:
                query = parse_qs(page[queryIndex+1:])
                for key in query.keys():
                    if len(query[key]) == 1:
                        self.REQUEST[key] = query[key][0]
                    else:
                        self.REQUEST[key] = query[key]
                page = page[0:queryIndex]

            trace.append("dispatchPage: page = " + str(page) + ", context = " + str(context))
#            self.log("page = " + str(page) + ", context = " + str(context), '_dispatchPage')
            return apply(context.restrictedTraverse(page), (context, context.REQUEST), kwargs)
        except Exception, e:
            raise NavigationError(e, trace)


    def _dispatchScript(self, context, script, trace, **kwargs):
        try:
#            self.log('calling ' + script, '_dispatchScript')

            request = {}
            for key in self.REQUEST.keys():
                request[key] = self.REQUEST[key]
            request.update(kwargs)

            script_object = getattr(context, script)

            trace.append('dispatchScript: script = %s' % (str(script)))
            (status, context, kwargs) = \
                mapply(script_object, self.REQUEST.args, request,
                            call_object, 1, missing_name, dont_publish_class,
                            self.REQUEST, bind=1)
#            self.log('status = %s, context = %s, kwargs = %s' % (str(status), str(context), str(kwargs)), '_dispatchScript')
            return self.getNext(context, script, status, trace, **kwargs)
        except Exception, e:
            raise NavigationError(e, trace)


    def _dispatchUrl(self, context, url, trace, **kwargs):
        try:
            url = self._addUrlArgs(url, kwargs)
            if len(urlparse(url)[1]) == 0:
                # no host specified -- url is relative
                # get an absolute url
                url = urljoin(context.absolute_url()+'/', url)
#            self.log('url = ' + str(url), '_dispatchUrl')
            trace.append('dispatchUrl: url = %s' % (str(url)))
            return self.REQUEST.RESPONSE.redirect(url)
        except Exception, e:
            raise NavigationError(e, trace)


    def _dispatchAction(self, context, action_id, trace, **kwargs):
        try:
            next_action = context.getTypeInfo().getActionById(action_id)
            url = self._addUrlArgs(next_action, kwargs)
#            self.log('url = ' + str(url), '_dispatchAction')
            trace.append('dispatchAction: url = %s' % (str(url)))
            return self.REQUEST.RESPONSE.redirect('%s/%s' % (context.absolute_url(), url))
        except Exception, e:
            raise NavigationError(e, trace)


    def _addUrlArgs(self, base, kwargs):
        url_params=urlencode(kwargs)
        if base.find('?') >= 0:
            separator = '&'
        else:
            separator = '?'
            if len(url_params) == 0:
                separator = ''
        return base+separator+url_params 


    def _normalize(self, st, lower=0):
        if st is None:
            return None
        st=st.replace(' ', '')        
        if lower:
            return st.lower()
        return st

    def _availableStatus(self):
        return ('success', 'failure')


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if loc is None:              
            debug_log(msg + ' - NavigationTool')
        else:
            debug_log(msg + ' - NavigationTool.'+loc)


    # DEPRECATED -- FOR BACKWARDS COMPATIBILITY WITH PLONE 1.0 ALPHA 2 ONLY
    # USE GETNEXT() INSTEAD AND UPDATE THE NAVIGATION PROPERTIES FILE
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, script, status, **kwargs):
        """ given a object, action_id and status we can fetch the next action
            for this object 
        """
        log_deprecated('NavigationTool.getNextPageFor() has been marked for deprecation')
        (transition_type, action_id) = self.getNavigationTransition(context,script,status)
        
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
        raise KeyError, 'Could not find the transition, ' + navTransition

    # DEPRECATED -- FOR BACKWARDS COMPATIBILITY WITH PLONE 1.0 ALPHA 2 ONLY
    # USE GETNEXT() INSTEAD AND UPDATE THE NAVIGATION PROPERTIES FILE
    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, script, status, **kwargs):
        """ takes object, script, and status and returns a RESPONSE redirect """
        log_deprecated('NavigationTool.getNextRequestFor() has been marked for deprecation')
        (transition_type, action_id) = self.getNavigationTransition(context,script,status) ###
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


class NavigationError(Exception):
    RE_BAD_VALIDATOR = re.compile("\'None\' object has no attribute \'co_varnames\'")

    def __init__(self, exception, trace):
        self.exception = exception
        self.trace = '\n'.join(trace) + '\n\n' + ''.join(traceback.format_exception(*sys.exc_info()))

    def __str__(self):
        return '<pre>' + str(self.exception) + '\n\nNavigation trace:\n-----------------' + self.trace + self._helpfulHints() + '</pre>'

    def _helpfulHints(self):
        st = str(self.exception)
        hint = ''
        if self.RE_BAD_VALIDATOR.search(st):
            hint = hint + 'The script or validator on which mapply is operating may not be compiling properly.\n'
        if hint:
            hint = '\n\nHelpful Hints:\n--------------\n' + hint
        return hint
