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
  When I add a redirect to the test folder from alternative url  /old
  Then I get redirected to the test folder when visiting  /old


Scenario: Remove redirect in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
  When I add a redirect to the test folder from alternative url  /old
   and I remove the redirect from alternative url  /old
  Then I do not get redirected when visiting  /old


Scenario: Remove filtered redirects in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
  When I add a redirect to the test folder from alternative url  /a
   and I add a redirect to the test folder from alternative url  /b
   and I filter the redirects with path  /a
   and I remove the matching redirects
  Then I do not get redirected when visiting  /a
   and I get redirected to the test folder when visiting  /b


Scenario: Download all redirects in the URL Management Control Panel
  Given a logged-in site administrator
    and the URL Management control panel
  When I add a redirect to the test folder from alternative url  /a
   and I add a redirect to the test folder from alternative url  /b
  Then I can download all redirects as CSV


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the URL Management control panel
  Go to  ${PLONE_URL}/@@redirection-controlpanel


# --- WHEN -------------------------------------------------------------------

I add a redirect to the test folder from alternative url
  [Documentation]  target path must exist in the site
  [Arguments]  ${old}
  Input Text  name=redirection  ${old}
  Input Text  name=target_path  /test-folder
  Click Button  Add


I remove the redirect from alternative url
  [Arguments]  ${old}
  Select Checkbox  xpath=//input[@value='/plone${old}']
  Click Button  Remove selected


I filter the redirects with path
  [Arguments]  ${old}
  Input Text  name=q  ${old}
  Click Button  Filter

I remove the matching redirects
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


I can download all redirects as CSV
  [Documentation]  I don't know how to get the contents of the downloaded file
  Click Button  Download all as CSV
  Page Should Not Contain  there seems to be an error
