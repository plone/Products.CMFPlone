*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

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


*** Keywords ***

# GIVEN

the URL Management control panel
    Go to  ${PLONE_URL}/@@redirection-controlpanel


# WHEN

I add a redirect to the test folder from alternative url
    [Documentation]  target path must exist in the site
    [Arguments]    ${old}
    Type Text    //input[@name="redirection"]    ${old}
    Type Text    //input[@name="target_path"]    /test-folder
    Click    //button[@name="form.button.Add"]


I remove the redirect from alternative url
    [Arguments]  ${old}
    Check Checkbox    //input[@value="/plone${old}"]
    Click    //button[@name="form.button.Remove"]

I filter the redirects with path
    [Arguments]    ${old}
    Type Text    //input[@name="q"]    ${old}
    Click    //button[@name="form.button.filter"]

I remove the matching redirects
    Click    //button[@name="form.button.MatchRemove"]


# THEN

I get redirected to the test folder when visiting
    [Arguments]    ${old}
    Go to    ${PLONE_URL}/${old}
    Get Url    should be    ${PLONE_URL}/test-folder


I do not get redirected when visiting
    [Arguments]    ${old}
    Go to    ${PLONE_URL}/${old}
    Get Url    should be    ${PLONE_URL}/${old}
    Get Text    //body    contains    This page does not seem to exist


I can download all redirects as CSV
    [Documentation]  Test the download of CSV file

    Import library    OperatingSystem

    ${dl_promise}    Promise To Wait For Download    saveAs=redirections.csv
    Click    //button[@name="form.button.Download"]
    ${file_obj}=    Wait For    ${dl_promise}
    File Should Exist    ${file_obj}[saveAs]
