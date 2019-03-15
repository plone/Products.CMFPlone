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
  When I Add A Redirect To The Test Folder From Alternative Url  /old
  Then I get redirected to the test folder when visiting  /old


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the URL Management control panel
  Go to  ${PLONE_URL}/@@redirection-controlpanel


# --- WHEN -------------------------------------------------------------------

I Add A Redirect To The Test Folder From Alternative Url
  [Documentation]  target path must exist in the site
  [Arguments]  ${old}
  Input Text  name=redirection  ${old}
  Input Text  name=target_path  /test-folder
  Click Button  Add


# --- THEN -------------------------------------------------------------------

I get redirected to the test folder when visiting
  [Arguments]  ${old}
  Go to  ${PLONE_URL}/${old}
  Location Should Be  ${PLONE_URL}/test-folder
