## Script (Python) "metadata_edit"
##title=Update Content Metadata
##parameters=allowDiscussion=None,title=None,subject=None,description=None,contributors=None,effective_date=None,expiration_date=None,format=None,language=None,rights=None,redirect=1
REQUEST=context.REQUEST


def tuplify( value ):

    if not same_type( value, () ):
        value = tuple( value )

    temp = filter( None, value )
    return tuple( temp )


if title is None:
    title=REQUEST.get('field_title', context.Title())

if subject is None:
    subject=REQUEST.get('field_subject', context.Subject())

if description is None:
    description=REQUEST.get('field_description', context.Description())

if contributors is None:
    contributors=tuplify(REQUEST.get('field_contributors', context.Contributors()))
else:
    contributors=tuplify(contributors)
    
if effective_date is None:
    effective_date=REQUEST.get('field_effective_date', context.EffectiveDate())

if expiration_date is None:
    expiration_date=REQUEST.get('field_expiration_date', context.ExpirationDate())

if format is None:
    format=REQUEST.get('field_format', context.Format())

if language is None:
    language=REQUEST.get('field_language', context.Language())

if rights is None:
    rights=REQUEST.get('field_rights', context.Rights())

if allowDiscussion:
    if allowDiscussion.lower().strip()=='default': allowDiscussion=None
    elif allowDiscussion.lower().strip()=='off': allowDiscussion=0
    elif allowDiscussion.lower().strip()=='on': allowDiscussion=1
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
