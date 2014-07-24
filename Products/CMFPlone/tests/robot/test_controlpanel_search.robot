*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Enable Livesearch in the Search Control Panel
  Given a logged-in site administrator
    and a document 'My Document'
    and the search control panel
   When I enable livesearch
   Then then searching for 'My Document' will show a live search


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

the search control panel
  Go to  ${PLONE_URL}/@@search-controlpanel


# --- WHEN -------------------------------------------------------------------

I enable livesearch
  Select Checkbox  form.widgets.enable_livesearch:list
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

then searching for 'My Document' will show a live search
  Go to  ${PLONE_URL}
  Wait until page contains element  xpath=//input[@name='SearchableText']
  Input Text  name=SearchableText  My
  # XXX: The Live Search should be visible !!!
