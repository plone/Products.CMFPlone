*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Add redirect in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
   When I add a redirect
   Then the redirect works


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the URL Management control panel
  Go to  ${PLONE_URL}/@@redirection-controlpanel


# --- WHEN -------------------------------------------------------------------

I add a redirect
  Input Text  name=redirection  /old
  Input Text  name=target_path  /test-folder
  Click Button  Add


# --- THEN -------------------------------------------------------------------

the redirect works
  Go to  ${PLONE_URL}/old
  Location Should Be  ${PLONE_URL}/test-folder
