*** Keywords *****************************************************************

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
