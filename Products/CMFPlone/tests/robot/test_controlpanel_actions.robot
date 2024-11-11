*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

# hint: the `Sleep` Statement is needed for the `Disable autologin` and the commit in the DB, it takes a while

Scenario: Modify an existing action in Actions Control Panel
    Given a logged-in manager
      and the actions control panel
     When I modify an action title
      and Sleep    1
     Then anonymous users can see the new action title

Scenario: Reorder in Actions Control Panel
    Given a logged-in manager
      and the actions control panel
     When I change the actions order
      and Sleep    1
     Then anonymous users can see the actions new ordering

Scenario: Create a new action in Actions Control Panel
    Given a logged-in manager
      and the actions control panel
     When I add a new action
      and Sleep    1
     Then logged-in users can see the new action

Scenario: Hide/show an action in Actions Control Panel
    Given a logged-in manager
      and the actions control panel
    When I hide an action
      and Sleep  1
    Then anonymous users cannot see the action anymore
    Given a logged-in manager
      and the actions control panel
    When I unhide the action
      and Sleep  1
    Then anonymous users can see the action again

Scenario: Delete an action in Actions Control Panel
    Given a logged-in manager
      and the actions control panel
     When I delete an action
      and Sleep  1
     Then anonymous users cannot see the action anymore

*** Keywords ***

# GIVEN

the actions control panel
    Go to    ${PLONE_URL}/@@actions-controlpanel
    Get Text    //body    contains    Portal actions

# WHEN

I modify an action title
    Click    //*[@id="content-core"]/section[2]/section/ol/li[1]/form/a
    Wait For Condition    Text    //body    contains    Action Settings
    Type Text    //input[@name="form.widgets.title"]    A new site map
    Click    //div[contains(@class,'pattern-modal-buttons')]/button


I change the actions order
    Click    //*[@id="content-core"]/section[2]/section/ol/li[1]/form/a
    Wait For Condition    Text    //body    contains    Action Settings
    Type Text    //input[@name="form.widgets.position"]    3
    Click    //div[contains(@class,'pattern-modal-buttons')]/button


I add a new action
    Click    //*[@id="content-core"]/p[@class="addAction"]/a
    Wait For Condition    Text    //body    contains    New action
    Select Options By    //select[@name="form.widgets.category:list"]    label    User actions
    Type Text    //input[@name="form.widgets.id"]    favorites
    Click    //div[contains(@class,'pattern-modal-buttons')]/button
    Wait For Condition    Text    //body    contains    favorites
    Click    //*[@id="content-core"]/section[6]/section/ol/li[9]/form/a
    Wait For Condition    Text    //body    contains    Action Settings
    Type Text    //input[@name="form.widgets.title"]    My favorites
    Type Text    //input[@name="form.widgets.url_expr"]    string:\${globals_view/navigationRootUrl}/favorites
    Click    //div[contains(@class,'pattern-modal-buttons')]/button


I hide an action
    Click    //*[@id="content-core"]/section[2]/section/ol/li[1]/form/button[@name="hide"]


I unhide the action
    Click    //*[@id="content-core"]/section[2]/section/ol/li[1]/form/button[@name="show"]


I delete an action
    Handle Future Dialogs    action=accept
    Click    //*[@id="content-core"]/section[2]/section/ol/li[1]/form/button[@name="delete"]


# THEN

anonymous users can see the new action title
    Disable autologin
    Go to    ${PLONE_URL}
    Get Text    //body    contains    A new site map


anonymous users can see the actions new ordering
    Disable autologin
    Go to  ${PLONE_URL}
    Get Element    //div[@id='portal-footer']//ul/li[1]/a/span[contains(text(), 'Accessibility')]
    Get Element    //div[@id='portal-footer']//ul/li[3]/a/span[contains(text(), 'Site Map')]


logged-in users can see the new action
    Disable autologin
    Enable autologin as   Contributor
    Go to  ${PLONE_URL}
    Get Element Count    //*[@id="personaltools-favorites"]    should be    1
    Get Text    //*[@id="personaltools-favorites"]    contains    My favorites


anonymous users cannot see the action anymore
    Disable autologin
    Go to  ${PLONE_URL}
    Get Text    //body    not contains    Site Map


anonymous users can see the action again
    Disable autologin
    Go to  ${PLONE_URL}
    Get Text    //body    contains    Site Map
