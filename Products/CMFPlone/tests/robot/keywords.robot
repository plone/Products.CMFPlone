*** Keywords *****************************************************************

# --- SETUP ------------------------------------------------------------------

Refresh JS/CSS resources
  # If we do not regenerate the resources meta-bundles, the baseUrl value in
  # config.js is http://foo/plone. We need to trigger the meta-bundles
  # generation from the browser so baseUrl gets the proper value.
  Enable autologin as  Manager
  # First visit a page, so that hopefully $ is defined in the line after it.
  # Not needed locally, but on Jenkins it might help.
  Go to  ${PLONE_URL}
  Execute Javascript    $.post($('body').attr('data-portal-url')+'/@@resourceregistry-controlpanel', {action: 'save-registry', _authenticator: $('input[name="_authenticator"]').val()});
  Disable Autologin

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator  Contributor  Reviewer

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

a file '${title}'
  Create content  type=File  id=file  title=${title}

a news item '${title}'
  Create content  type=News Item  id=doc  title=${title}

an image '${title}'
  Create content  type=Image  id=doc  title=${title}

a folder '${title}'
  Create content  type=Folder  title=${title}

patterns are loaded
  Wait For Condition  return $('body.patterns-loaded').size() > 0

a folder with a document '${title}'
  ${folder_uid}=  Create content  type=Folder  title=folder
  Create content  type=Document  container=${folder_uid}  title=${title}
