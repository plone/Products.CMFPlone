## Script (Python) "collector_transcript_view.py"
##title=Redirect to the issue containing the transcript

context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())

