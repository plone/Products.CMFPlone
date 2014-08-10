*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Change Default Markup Types in the Markup Control Panel
  Given a logged-in site administrator
    and the markup control panel
   When I set allowed types to "text/html"
   Then I can see only "text/html" when editing a document

Scenario: Set Default Markup to be Restructured Text
  Given a logged-in site administrator
    and the editing control panel
   When I set the default type to "text/rst"
   Then I do not see the standard editor when I create a document


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

the editing control panel
  Go to  ${PLONE_URL}/@@editing-controlpanel


# --- WHEN -------------------------------------------------------------------

I enable visible ids
  Select Checkbox  form.widgets.visible_ids:list
  Click Button  Save
  Wait until page contains  Changes saved

I disable the standard editor
  Select from list by label  name=form.widgets.default_editor:list  None
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

I can see an id field in the settings tab when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Input Text  name=form.widgets.IDublinCore.title  My Document
  Click Link  Settings
  Page should contain element  name=form.widgets.IShortName.id
  Input Text  name=form.widgets.IShortName.id  this-is-my-custom-short-name
  Click Button  Save
  Wait until page contains  Item created
  Location should be  ${PLONE_URL}/this-is-my-custom-short-name/view

I do not see the standard editor when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Page should not contain element  css=.mce-tinymce

