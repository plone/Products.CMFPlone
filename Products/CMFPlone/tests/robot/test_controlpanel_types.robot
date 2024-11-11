*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***
Scenario: Change default workflow
    Given a logged-in site administrator
      and the types control panel
     When I select 'Single State Workflow' workflow
      and I add new Link 'my_link'
     Then Link 'my_link' should have Single State Workflow enabled


*** Keywords ***

# GIVEN
the types control panel
    Go to    ${PLONE_URL}/@@content-controlpanel
    Get Text    //body    contains    Content Settings


# WHEN
I select '${workflow}' workflow
    Select Options By    //select[@name="new_workflow"]    label    ${workflow}
    Click    //button[@name="form.button.Save"]
    Wait For Condition    Text    //body    contains   Content Settings


I add new Link '${id}'
    Go to    ${PLONE_URL}
    Create content
    ...    type=Link
    ...    id=${id}
    ...    title=${id}
    ...    remoteUrl=https://www.plone.org


# THEN

Link '${id}' should have Single State Workflow enabled
    Go to    ${PLONE_URL}/${id}
    # We check that single state worklow is used, publish button is not present
    Get Element Count    //a[@id="workflow-transition-publish"]    should be    0
