*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

a folder '${title}'
  Create content  type=Folder  title=${title}

patterns are loaded
  Wait For Condition  return $('body.patterns-loaded').size() > 0

a folder with a document '${title}'
  ${folder_uid}=  Create content  type=Folder  title=folder
  Create content  type=Document  container=${folder_uid}  title=${title}
