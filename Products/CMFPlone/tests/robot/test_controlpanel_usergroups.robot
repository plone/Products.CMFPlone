# ============================================================================
# Tests for the Plone Usergroups Control Panel
# ============================================================================
#
# $ bin/robot-server --reload-path src/Products.CMFPlone/Products/CMFPlone/ Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
#
# $ bin/robot src/Products.CMFPlone/Products/CMFPlone/tests/robot/test_controlpanel_usergroups.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Show all users in users control panel
  Given a logged-in site administrator
    and the usergroups control panel
   When I click show all users
   Then all users should be shown

Scenario: Show all groups in groups control panel
  Given a logged-in site administrator
    and the usergroups control panel
   When I go to Groups control panel
    and I click show all groups
   Then all groups should be shown

Scenario: Create new group
  Given a logged-in site administrator
    and the usergroups control panel
   When I go to Groups control panel
    and I create new group
   Then new group should show under all groups

Scenario: Enable many groups and many users settings in usergroups control panel
  Given a logged-in site administrator
    and the usergroups control panel
   When I go to Settings control panel
    and enable many groups and many users settings
   Then showing all users is disabled
    and showing all groups is disabled


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the usergroups control panel
  Go to  ${PLONE_URL}/@@usergroup-userprefs
  Wait until page contains  Users and Groups


# --- WHEN -------------------------------------------------------------------

I click show all users
  Click button  Show all
  Wait until page contains  User Search

I go to Groups control panel
  Click link  xpath=//*[@id='content']//header//a[contains(text(), 'Groups')]
  Wait until page contains  Group Search

I click show all groups
  Click button  Show all
  Wait until page contains  Group Search

I create new group
  Click button  Add New Group
  Wait until page contains element  name=addname
  patterns are loaded
  Input Text  name=addname  my-new-group
  Input Text  name=title:string  My New Group
  Input Text  name=description:text  This is my new group
  Input Text  name=email:string  my-group@plone.org
  Submit Form  id=createGroup
#  "Click button  Save" does not work for modals. See https://stackoverflow.com/questions/17602334/element-is-not-currently-visible-and-so-may-not-be-interacted-with-but-another for details.
  I click show all groups
  Page should contain  my-new-group

I go to Settings control panel
  Click link  Settings
  Wait until page contains  User and groups settings

enable many groups and many users settings
  Select Checkbox  name=form.widgets.many_groups:list
  Select Checkbox  name=form.widgets.many_users:list
  Click button  Save
  Wait until page contains  Data successfully updated.

# --- THEN -------------------------------------------------------------------

all users should be shown
  Page should contain  test-user
  Page should contain  admin

all groups should be shown
  Page should contain  Administrators
  Page should contain  Authenticated Users (Virtual Group) (AuthenticatedUsers)
  Page should contain  Reviewers
  Page should contain  Site Administrators

showing all users is disabled
  Click link  xpath=//*[@id='content']//header//a[contains(text(), 'Users')]
  Wait until page contains  User Search
  Page should not contain  Show all

showing all groups is disabled
  Click link  xpath=//*[@id='content']//header//a[contains(text(), 'Groups')]
  Wait until page contains  Group Search
  Page should not contain  Show all

new group should show under all groups
  Page should contain  my-new-group
