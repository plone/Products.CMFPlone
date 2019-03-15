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


Scenario: Remove redirect in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
  When I Add A Redirect To The Test Folder From Alternative Url  /old
   and I Remove The Redirect From Alternative Url  /old
  Then I do not get redirected when visiting  /old


Scenario: Remove filtered redirects in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
  When I Add A Redirect To The Test Folder From Alternative Url  /a
   and I Add A Redirect To The Test Folder From Alternative Url  /b
   and I Filter The Redirects With Path  /a
   and I Remove The Matching Redirects
  Then I do not get redirected when visiting  /a
   and I get redirected to the test folder when visiting  /b


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


I Remove The Redirect From Alternative Url
  [Arguments]  ${old}
  Select Checkbox  xpath=//input[@value='/plone${old}']
  Click Button  Remove selected


I Filter The Redirects With Path
  [Arguments]  ${old}
  Input Text  name=q  ${old}
  Click Button  Filter

I Remove The Matching Redirects
  Click Button  Remove all that match filter


# --- THEN -------------------------------------------------------------------

I get redirected to the test folder when visiting
  [Arguments]  ${old}
  Go to  ${PLONE_URL}/${old}
  Location Should Be  ${PLONE_URL}/test-folder


I do not get redirected when visiting
  [Arguments]  ${old}
  Go to  ${PLONE_URL}/${old}
  Location Should Be  ${PLONE_URL}/${old}
  Wait Until Page Contains  This page does not seem to exist
