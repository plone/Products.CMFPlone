from ZPublisher.mapply import mapply
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from Products.CMFPlone import ToolNames
from Acquisition import Implicit
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
from ZODB.POSException import ConflictError

from interfaces.NavigationController import INavigationController

debug = 0  # enable/disable logging

def custom_missing_name(name, request):
    if name=='self': return request['PARENTS'][0]
    raise 'Invalid request', 'The parameter %s is missing.' % name

class NavigationTool(UniqueObject, SimpleItem):
    """ provides navigation related utilities """

    id = 'portal_navigation'
    meta_type = ToolNames.NavigationTool
    toolicon = 'skins/plone_images/error_icon.gif'

    security = ClassSecurityInfo()
    plone_tool = 1
    __implements__ = INavigationController,

    security.declarePublic('getNext')
    def getNext(self, context, script, status, trace=[], **kwargs):

        """ Perform the next action specified by in
        portal_properties.navigation_properties.  Get the object that
        will perform the next action, then call the object to perform
        the next action.

        context - the current context

        script - the script/template currently being called

        status - 'success' or 'failure' strings used in calculating destination

        kwargs - additional keyword arguments are passed to subsequent
        pages either in the REQUEST or as GET parameters if a
        redirection needs to be done

        trace - navigation trace for internal use
        """
        try:
            trace.append(('Getting next object for %s.%s.%s'
                          ) % (context, script, status))
            (obj, kwargs) = self.getNextObject(context, script,
                                               status, trace, **kwargs)
            return apply(obj, (), {'REQUEST':context.REQUEST})
        except ConflictError:
            raise
        except:
            self.logTrace(trace)
            raise


    security.declarePublic('getNextObject')
    def getNextObject(self, context, script, status, trace=[], **kwargs):

        """ Get the object that will perform the next action specified
        by portal_properties.navigation_properties.  Returns an object
        that can be placed on the traversal stack so that it will get
        called during publishing.

        context - the current context

        script - the script/template currently being called

        status - 'success' or 'failure' strings used in calculating destination

        kwargs - additional keyword arguments are passed to subsequent
        pages either in the REQUEST or as GET parameters if a
        redirection needs to be done

        trace - navigation trace for internal use
        """
        try:
            trace.append(('Looking up transition for %s.%s.%s'
                          ) % (context, script, status))
            (transition_type, redirect, transition) = (
                self.getNavigationTransition(context, script,
                                             status))
            trace.append(('Found transition: %s, %s'
                          ) % (transition_type, transition))
            self.log(trace,'getNextObject')
            self.log("%s.%s.%s(%s) -> %s:%s" % (context, script, status,
                                                str(kwargs), transition_type,
                                                transition), 'getNextObject')

            if transition_type == 'action':
                return self._getAction(context, transition, redirect,
                                       trace, **kwargs)
            elif transition_type == 'url':
                return self._getUrl(context, transition, redirect,
                                    trace, **kwargs)
            elif transition_type == 'script':
                return self._getScript(context, transition, redirect,
                                       trace, **kwargs)
            else:
                raise KeyError('Unknown transition type %s' % transition_type)
        except ConflictError:
            raise
        except:
            self.logTrace(trace)
            raise


    def addTransitionFor(self, content, script, status, destination):
        """ Adds a transition.  When SCRIPT with context CONTENT
        returns STATUS, go to DESTINATION

        content - is a object or a TypeInfo that you would like to
        register.  A None content object will register
        Default values.

        script - the script/template that was just called

        status - SUCCESS or FAILURE strings used in calculating destination

        destination - is an action registed on the TypeInfo or a free-form script
        that would be appended to the url of the content

        Destinations are specified as follows: action:ACTION_NAME
        invokes the action ACTION_NAME on the current context
        script:SCRIPT_NAME invokes the python script SCRIPT_NAME on
        the current context.  The script should return a tuple
        containing a status code (either 'success' or 'failure') and
        optional kwargs.  getNext() will be called using the return
        code to determine the next page to load.  url:URL redirects to
        the url specified by URL.  URL may be absolute or relative
        PAGE invokes the page PAGE on the current context
        """

        property_tool = getattr(self, 'portal_properties')
        #propertymanager that holds data
        navprops = getattr(property_tool, 'navigation_properties')

        content=self._getContentFrom(content)
        status = self._normalize(status, lower=1)
        script = self._normalize(script)

        transition = '%s.%s.%s'%( content
                                , script
                                , status )

        if navprops.hasProperty(transition):
            navprops._updateProperty(transition, destination)
        else:
            navprops._setProperty(transition, destination)


    security.declarePrivate('removeTransitionFrom')
    def removeTransitionFrom(self, content, script=None, status=None):
        """ removes everything regarding a content/script combination """

        property_tool = getattr(self, 'portal_properties')
        #propertymanager that holds data
        navprops = getattr(property_tool, 'navigation_properties')
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
            content = content.getTypeInfo()
        if hasattr(content, 'getId'): #XXX use a xface
            content = content.getId()
        # handle types without getTypeInfo (e.g. CMFSite)
        if type(content) != type(''):
            content = 'Default'
        content = self._normalize(content, lower=1) #normalize
        return content


    # Transitions are determined by a set of actions listed in a
    # properties file.  One can include information from the REQUEST
    # into a transition by using an expression enclosed in brackets,
    # i.e. something of the form [foo].  The bracketed expression will
    # be replaced by REQUEST['foo'], or an empty string if the REQUEST
    # has no key 'foo'.  To specify an alternative action in the event
    # that the REQUEST has no key 'foo', use [foo|bar].  If
    # REQUEST.foo doesn't exist, then the bracketed expression is
    # replaced by bar.
    #
    # Example: document.document_edit.success:string=view?came_from=[came_from|/]
    #
    # Regular expression used for performing substitutions in
    # navigation transitions:
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


    # parse a transition into a transition type, a redirect flag, and an argument
    def _parseTransition(self, transition):
        transition_types = [  {'id':'action', 'default_redirect':1}
                            , {'id':'url', 'default_redirect':1}
                            , {'id':'script', 'default_redirect':0}
                           ]

        redirect = None
        if transition.startswith('redirect:'):
            redirect = 1
            transition = transition[len('redirect:'):]
        elif transition.startswith('noredirect:'):
            redirect = 0
            transition = transition[len('noredirect:'):]

        for t in transition_types:
            if transition.startswith(t['id']+':'):
                if redirect == None:
                    redirect = t['default_redirect']
                return (t['id'], redirect, transition[len(t['id'])+1:].strip())
        if redirect == None:
            redirect = 0
        return ('url', redirect, transition.strip())


    def getNavigationTransition(self, context, script, status):
        script = self._normalize(script) # normalize
        status = self._normalize(status) # normalize

        property_tool = getattr(self, 'portal_properties')
        navprops = getattr(property_tool, 'navigation_properties')

        transition_key = self._getContentFrom(context)+'.'+script+'.'+status
        transition = getattr(navprops.aq_explicit, transition_key, None)

        if transition is None:
            transition_key = ('%s.%s.%s'
                              ) % (self._getContentFrom(None), script, status)
            transition = getattr(navprops.aq_explicit, transition_key, None)

            if transition is None:
                transition_key= '%s.%s.%s' % (self._getContentFrom(None),
                                             'default', status)
                transition = getattr(navprops.aq_explicit, transition_key, None)

                if transition is None:
                    raise KeyError, (
                        "Unable to find navigation transition for %s.%s.%s"
                        ) % (self._getContentFrom(context), script, status)

        self.log(("getting transition %s.%s.%s, found [%s]\n"
                  ) % (context, script, status, str(transition)))

        transition = self._transitionSubstitute(transition, self.REQUEST)
        return self._parseTransition(transition)

    def _getScript(self, context, script, redirect, trace, **kwargs):
        if redirect:
            return self._getUrl(context, script, redirect, trace, **kwargs)
        try:
            self.log('calling ' + script, '_getScript')
            trace.append('_getScript: script = %s' % (str(script)))

            request = {}
            for key in self.REQUEST.keys():
                request[key] = self.REQUEST[key]
            request.update(kwargs)

            script_object = getattr(context, script, None)
            if script_object is None:
                raise KeyError, (
                    "Unable to find script '%s' in context '%s'."
                    "Check your skins path.") % (script, str(context))

            script_status = mapply(script_object, self.REQUEST.args, request,
            call_object, 1, custom_missing_name, dont_publish_class,
            self.REQUEST, bind=1)

            # The preferred return type for scripts will eventually be an object.
            # Until then, preserve compatibility with 1.0 alpha 4
            if type(script_status) == type(()):
                (status, new_context, kwargs) = script_status
                script_status = ScriptStatus(status, kwargs, new_context)
                # disable deprecation warning for now
                # log_deprecated("""Script \'%s\' uses a return signature that
                #              has been marked for deprecation.  Scripts
                #              should return a ScriptStatus object.""" % script)

            status = script_status.status
            kwargs = script_status.kwargs
            new_context = script_status.new_context
            if new_context is None:
                new_context = context
            self.log(('status = %s, new_context = %s, kwargs = %s'
                      ) % (str(status), str(new_context),
                           str(kwargs)), '_getScript')

            return self.getNextObject(new_context, script, status,
                                      trace, **kwargs)
        except ConflictError:
            raise
        except:
            self.logTrace(trace)
            raise


    def _getUrl(self, context, url, redirect, trace, **kwargs):
        try:
            if redirect:
                # don't pass along errors to subsequent forms
                if kwargs.has_key('errors'):
                    del kwargs['errors']
                url = self._addUrlArgs(url, kwargs)
                if len(urlparse(url)[1]) == 0:
                    # no host specified -- url is relative
                    # get an absolute url
                    url = urljoin(context.absolute_url()+'/', url)
                self.log(("url = %s, redirect = %s, context = %s"
                          ) % (str(url), str(redirect), str(context)), '_getUrl')
                trace.append(("_getUrl: url = %s, redirect = %s, context = %s"
                              ) % (str(url), str(redirect), str(context)))
                return (Redirector(url), kwargs)
            else:
                # If any query parameters have been specified in the transition,
                # stick them into the request before calling getActionById()
                queryIndex = url.find('?')
                if queryIndex > -1:
                    query = parse_qs(url[queryIndex+1:])
                    for key in query.keys():
                        if len(query[key]) == 1:
                            self.REQUEST[key] = query[key][0]
                        else:
                            self.REQUEST[key] = query[key]
                    url = url[0:queryIndex]
                # put kwargs into REQUEST -- kwargs override args in url
                if kwargs:
                    for key in kwargs.keys():
                        self.REQUEST[key] = kwargs[key]

                self.log(("url = %s, redirect = %s, context = %s"
                          ) % (str(url), str(redirect), str(context)), '_getUrl')
                trace.append(("_getUrl: url = %s, redirect = %s, context = %s"
                              ) % (str(url), str(redirect), str(context)))
                return (context.restrictedTraverse(url), kwargs)
        except ConflictError:
            raise
        except:
            self.logTrace(trace)
            raise


    def _getAction(self, context, action_id, redirect, trace, **kwargs):
        try:
            next_action = context.getTypeInfo().getActionById(action_id)
            trace.append('_getAction: next_action = %s' % (str(next_action)))
            if next_action is None:
                raise KeyError, ("Unknown action '%s' for type %s."
                                 ) % (action_id, context.getTypeInfo().getId())
            # make sure we don't end up with nested portal_form calls
            if next_action.startswith('portal_form/') and \
                   context.REQUEST.URL.find('portal_form') != -1:
                next_action = next_action[len('portal_form/'):]
            return self._getUrl(context, next_action, redirect, trace, **kwargs)
        except ConflictError:
            raise
        except:
            self.logTrace(trace)
            raise


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


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        props = getToolByName(self, 'portal_properties')
        site_props = props.site_properties
        debug = getattr(site_props, 'enable_navigation_logging', 0)

        if not debug:
            return
        prefix = 'NavigationTool'
        if loc:
            prefix = prefix + '. ' + str(loc)
        debug_log(prefix+': '+str(msg))


    RE_BAD_SCRIPT = re.compile("\'None\' object has no attribute \'co_varnames\'")

    def logTrace(self, trace, clearTrace=1):
        if trace:
            formattedTrace = '\n'.join(trace)+'\n\n'
            pt = getToolByName(self, 'plone_utils')
            exceptionString = pt.exceptionString()
            hint = ''
            if self.RE_BAD_SCRIPT.search(exceptionString):
                hint = hint + 'The script or validator on which mapply'\
                       'is operating may not be compiling properly.\n'
            import zLOG
            zLOG.LOG('Plone: ', 0, ('%s \n\nNavigation trace: (version %s)'
                                    '\n-----------------\n%s%s'
                                    ) % (exceptionString,
                                         __version__.strip(),
                                         formattedTrace,
                                         hint))
            if clearTrace:
                # clear out the trace so that logging is only done
                # once up the exception stack
                del trace[0:len(trace)]


    # DEPRECATED -- FOR BACKWARDS COMPATIBILITY WITH PLONE 1.0 ALPHA 2 ONLY
    # USE GETNEXT() INSTEAD AND UPDATE THE NAVIGATION PROPERTIES FILE
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, script, status, **kwargs):
        """ Given a object, action_id and status we can fetch the next
            action for this object """

        log_deprecated('NavigationTool.getNextPageFor() has'\
                       'been marked for deprecation')
        (transition_type, redirect, action_id) = (
            self.getNavigationTransition(context, script, status))

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
        """ Takes object, script, and status and returns a RESPONSE
        redirect """

        log_deprecated('NavigationTool.getNextRequestFor() has'\
                       'been marked for deprecation')
        (transition_type, action_id) = self.getNavigationTransition(context,
                                                                    script,
                                                                    status)
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


# Eventually this object will be the preferred return type for scripts
# that are handled by the navigation machinery.

class ScriptStatus:
    def __init__(self, status, kwargs = {}, new_context = None):
        self.status = status
        self.kwargs = kwargs
        self.new_context = new_context


class Redirector(SimpleItem):
    """
    Placeholder object for a redirect.  When a Redirector is placed in the
    traversal stack, it will result in a redirect.  Note that the Redirector
    does not need to be at the end of the stack -- if it is not, it will cut
    traversal short so that it ends up at the end of the stack.  Redirector
    objects are used by NavigationTool and FactoryTool.
    """
    security = ClassSecurityInfo()

    def __init__(self, url):
        self.url = url


    def __before_publishing_traverse__(self, other, REQUEST):
        # prevent further traversal
        REQUEST.set('TraversalRequestNameStack', [])


    security.declarePublic('__call__')
    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        """ """
        if RESPONSE:
            response = RESPONSE
        else:
            response = REQUEST.RESPONSE
        return response.redirect(self.url)


    index_html = None  # call __call__, not index_html


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        prefix = 'Redirector'
        if loc:
            prefix = prefix + '. ' + str(loc)
        debug_log(prefix+': '+str(msg))

InitializeClass(Redirector)
