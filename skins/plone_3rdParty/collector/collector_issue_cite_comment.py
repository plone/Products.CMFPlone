## Script (Python) "collector_issue_cite_comment.py"
##parameters=
##title=Redirect to issue contents with cite parameter
 
context.REQUEST.RESPONSE.redirect(context.absolute_url()
                                  + '?do_cite=1#comment')

