from Interface import Base

class INavigationController(Base):
    """ The NavigationController acts as a controller that controls complex states of the system.
    
        The interface provides ways for getNext() transition (where to go next) as well as how
        to add/remove transitions (complex states) from the object.
    """
    
    def getNext(context, script, status, trace, **kwargs):
        """ Perform the next action specified by in portal_properties.navigation_properties.

            context - the current context

            script - the script/template currently being called

            status - 'success' or 'failure' strings used in calculating destination

            kwargs - additional keyword arguments are passed to subsequent pages either in
                     the REQUEST or as GET parameters if a redirection needs to be done

            trace - navigation trace for internal use
        """

    def addTransitionFor(content, script, status, destination):
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
                                      or 'failure') and optional kwargs.                                                                                                                getNext() will be called using the return code to determine the next page
                                      to load.
                              url:URL redirects to the url specified by URL.  URL may be absolute or relative
                              PAGE invokes the page PAGE on the current context
       """
    
    def removeTransitionFrom(content, script=None, status=None):
       """ Removes all participating transitions involvd with a content/script interaction """
    
