## Script (Python) "metadata_edit"
##title=Update Content Metadata
##parameters=allowDiscussion=None,title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None,redirect=1
REQUEST=context.REQUEST

if not title: title=REQUEST.get('field_title', None)
if not subject: subject=REQUEST.get('field_subject', None)
if not description: description=REQUEST.get('field_description', None)
if not contributors: contributors=REQUEST.get('field_contributors', None)
if not effective_date: effective_date=REQUEST.get('field_effective_date', None)
if not expiration_date: expiration_date=REQUEST.get('field_expiration_date', None)
if not format: format=REQUEST.get('field_format', None)
if not language: language=REQUEST.get('field_language', None)
if not rights: rights=REQUEST.get('field_rights', None)

def tuplify( value ):

    if not same_type( value, () ):
        value = tuple( value )

    temp = filter( None, value )
    return tuple( temp )

if title is None:
    title = context.Title()

if subject is None:
    subject = context.Subject()
else:
    subject = tuplify( subject )

if description is None:
    description = context.Description()

if contributors is None:
    contributors = context.Contributors()
else:
    contributors = tuplify( contributors )

if effective_date is None:
    effective_date = context.EffectiveDate()

if expiration_date is None:
    expiration_date = context.expires()

if format is None:
    format = context.Format()

if language is None:
    language = context.Language()

if rights is None:
    rights = context.Rights()

if allowDiscussion:
    context.portal_discussion.overrideDiscussionFor(context, allowDiscussion)

try:  
    context.editMetadata( title=title
                        , description=description
                        , subject=subject
                        , contributors=contributors
                        , effective_date=effective_date
                        , expiration_date=expiration_date
                        , format=format
                        , language=language
                        , rights=rights
                        )
    try:
        action_path = context.getTypeInfo().getActionById( 'edit' )
    except:
        action_path = context.getTypeInfo().getActionById( 'view' )   

    if redirect:
        context.REQUEST['RESPONSE'].redirect(
                  '%s/%s?portal_status_message=Metadata+changed.'
                    % ( context.absolute_url(), action_path ) )
except Exception, msg:
    target_action = context.getTypeInfo().getActionById( 'metadata' )
    if redirect:
        context.REQUEST.RESPONSE.redirect('%s/%s?portal_status_message=%s' % (
                                                                              context.absolute_url()
                                                                            , target_action
                                                                            , msg
                                                                             ))
