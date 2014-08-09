*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Enable Visible IDs in the Editing Control Panel
  Given a logged-in site administrator
    and the editing control panel
   When I enable visible ids
   Then I can see an id field when I create a document


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


# --- THEN -------------------------------------------------------------------

I can see an id field when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Input Text  name=form.widgets.IDublinCore.title  My Document
  Click Link  Settings
  Page should contain element  name=form.widgets.IShortName.id
  Input Text  name=form.widgets.IShortName.id  this-is-my-custom-short-name
  Click Button  Save
  Wait until page contains  Item created
  Location should be  ${PLONE_URL}/this-is-my-custom-short-name/view
