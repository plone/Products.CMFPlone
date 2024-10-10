*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Show all users in users control panel
    Given a logged-in site administrator
      and the users control panel
     When I click show all users
     Then all users should be shown

Scenario: Show all groups in groups control panel
    Given a logged-in site administrator
      and the groups control panel
     When I click show all groups
     Then all groups should be shown

Scenario: Create new group
    Given a logged-in site administrator
      and the groups control panel
     When I create new group
      and I click show all groups
     Then new group should show under all groups

Scenario: Enable many groups and many users settings in usergroups control panel
    Given a logged-in site administrator
      and the user group settings control panel
     When I enable many groups and many users settings
     Then showing all users is disabled
      and showing all groups is disabled


*** Keywords ***

# GIVEN

the users control panel
    Go to    ${PLONE_URL}/@@usergroup-userprefs
    Get Text    //body    contains    User Search

the groups control panel
    Go to    ${PLONE_URL}/@@usergroup-groupprefs
    Get Text    //body    contains    Group Search

the user group settings control panel
    Go to    ${PLONE_URL}/@@usergroup-controlpanel
    Get Text    //body    contains    User and Groups Settings


# WHEN

I click show all users
    Click    //button[@name="form.button.FindAll"]
    Get Text    //body    contains    User Search

I click show all groups
    Click    //button[@name="form.button.FindAll"]
    Get Text    //body    contains    Group Search

I create new group
    Click    //a[@id="add-group"]
    Type Text    //input[@name="addname"]    my-new-group
    Type Text    //input[@name="title:string"]    My New Group
    Type Text    //textarea[@name="description:text"]    This is my new group
    Type Text    //input[@name="email:string"]    my-group@plone.org
    Click    //form[@id="createGroup"]//button[@name="form.button.Save"]

I enable many groups and many users settings
    Check Checkbox    //input[@name="form.widgets.many_groups:list"]
    Check Checkbox    //input[@name="form.widgets.many_users:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Data successfully updated.

# THEN

all users should be shown
    Get Text    //body    contains    test-user
    Get Text    //body    contains    admin

all groups should be shown
    Get Text    //body    contains    Administrators
    Get Text    //body    contains    Authenticated Users (Virtual Group) (AuthenticatedUsers)
    Get Text    //body    contains    Reviewers
    Get Text    //body    contains    Site Administrators

showing all users is disabled
    the users control panel
    Get Text    //body    not contains    Show all

showing all groups is disabled
    the groups control panel
    Get Text    //body    not contains    Show all

new group should show under all groups
    Get Text    //body    contains    my-new-group
