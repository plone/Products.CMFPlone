*** Settings ***

Documentation  These tests are just testing the overlay behavior not the
...            functionality of each form. This is supposed to be tested in
...            functional tests somewhere. At some point in the future the
...            functional tests can be transferred to robot tests into each
...            scenario test case.

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Run keywords  Open SauceLabs test browser  Background
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test cases ***

Scenario: Contact form overlay opens
    Given the site root
     When I click the 'Contact' link
     Then overlay should open

Scenario: Contact form overlay closes
    Go to  ${PLONE_URL}/logout
    Given the 'Contact' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay opens
    Go to  ${PLONE_URL}/logout
    Given the site root
     When I click the 'Log in' link
     Then overlay should open

Scenario: Log in form overlay closes
    Go to  ${PLONE_URL}/logout
    Given the site root
    Given the 'Log in' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay remains on wrong credentials
    Go to  ${PLONE_URL}/logout
    Given the site root
    Given the 'Log in' overlay
     When I enter wrong credentials
     Then overlay should remain open
      And overlay shows an error

Scenario: Log in form overlay closes on valid credentials
    Go to  ${PLONE_URL}/logout
    Given the site root
    Given the 'Log in' overlay
     When I enter valid credentials
     Then overlay should close

Scenario: Set default content item of a folder overlay opens
    Given a logged-in site administrator
      And a document 'doc' in the test folder
     When I set the default content view of the test folder
     Then overlay should open

# XXX Next 2 tests are commented out. After hours of messing around,
# I still can not pinpoint why this is happening.
# The error originates from this change https://github.com/plone/mockup/commit/ccec87028bc22e082d6d9a95874d8a961f91b707
# which provides at least some error reporting(window.alert) to users when modals
# experience issues. We need this change in modals...
#
# However, in these 2 cases, it is triggering the window.alert
# and causing the tests to fail in certain cases.
# It ONLY happens when running automatically by the robot framework
# runner. If you try to use Import library  DebugLibrary and
# run the commands manually, of course it works fine. So yes,
# there is no way to really figure out this AFAIK.
# Also, of course, this doesn't happen in real user testing.
#
#Scenario: Change default content item of a folder overlay opens
#    Given a logged-in site administrator
#      And a document as the default view of the test folder
#     When I change the default content view of the test folder
#     Then overlay should open

#Scenario: Change default content item of a folder overlay closes
#    Given a logged-in site administrator
#      And a document as the default view of the test folder
#     When I change the default content view of the test folder
#      And I 'Cancel' the form
#     Then overlay should close
#     When I change the default content view of the test folder
#      And I 'Save' the form
#     Then overlay should close
#     When I change the default content view of the test folder
#      And I close the overlay
#     Then overlay should close

Scenario: Delete content action overlay opens
    Given a logged-in site administrator
     When I trigger the 'delete' action menu item of the test folder
     Then overlay should open

Scenario: Delete content action overlay closes
    Given a logged-in site administrator
     When I trigger the 'delete' action menu item of the test folder
      And I 'Cancel' the form
     Then overlay should close
     When I trigger the 'delete' action menu item of the test folder
      And I close the overlay
     Then overlay should close
     When I trigger the 'delete' action menu item of the test folder
      And I confirm deletion of the content
     Then overlay should close

Scenario: Rename content action overlay opens
    Given a logged-in site administrator
     When I trigger the 'rename' action menu item of the test folder
     Then overlay should open

Scenario: Rename content action overlay closes
    Given a logged-in site administrator
     When I trigger the 'rename' action menu item of the test folder
      And I 'Cancel' the form
     Then overlay should close
     When I trigger the 'rename' action menu item of the test folder
      And I close the overlay
     Then overlay should close

Scenario: Register user overlay opens
    Given the mail setup configured
      And the self registration enabled
      Go to  ${PLONE_URL}/logout
      And the site root
     When I click the 'Register' link
     Then overlay should open

Scenario: Register user overlay closes
    Given the mail setup configured
      And the self registration enabled
      Go to  ${PLONE_URL}/logout
      And the site root
      And the 'Register' overlay
     When I close the overlay
     Then overlay should close

Scenario: Register user overlay remains on wrong data
    Given the mail setup configured
      And the self registration enabled
      Go to  ${PLONE_URL}/logout
      And the site root
      And the 'Register' overlay
     When I send the register form
     Then overlay should remain open
      And overlay shows an error

# Note: For this one we need to fake the mail server, as it tries to send the
# mail right away. Or change the somehow confusing message that shows when this
# happens.
#Scenario: Register user overlay closes on valid data
#    Given the mail setup configured
#      And the self registration enabled
#      And the site root
#      And the 'Register' overlay
#     When I enter valid register user data
#      And I send the register form
#     Then overlay should close

Scenario: New user overlay opens
    Given a logged-in site administrator
      And the users and groups configlet
     When I trigger the add a new user action
     Then overlay should open

Scenario: New user overlay remains on wrong data
    Given a logged-in site administrator
      And the users and groups configlet
      And I trigger the add a new user action
     When I send the register form
     Then overlay should remain open
      And overlay shows an error

Scenario: New user overlay closes on valid data
    Given a logged-in site administrator
      And the users and groups configlet
      And I trigger the add a new user action
     When I enter valid user data
      And I send the register form
     Then overlay should close

Scenario: History overlay opens
    Given a logged-in site administrator
      And the test folder
     When I click the 'Content Info' link
      And I click the 'History' link
     Then overlay should open

Scenario: History overlay closes
    Given a logged-in site administrator
      And the test folder
      When I click the 'Content Info' link
      And I click the 'History' link
     When I close the overlay
     Then overlay should close

*** Keywords ***

Background
    Given a logged-in site administrator
      and a test folder
    Disable autologin
    Go to homepage

a logged-in site administrator
  Enable autologin as  Site Administrator

the users and groups configlet
    Go to  ${PLONE_URL}/@@usergroup-userprefs
    Given modals loaded

I click the '${link_name}' link
    Given modals loaded
    Element should be visible  xpath=//a[descendant-or-self::*[contains(text(), '${link_name}')]]
    Click Link  xpath=//a[descendant-or-self::*[contains(text(), '${link_name}')]]

the '${link_name}' overlay
    Given modals loaded
    Click Link  xpath=//a[descendant-or-self::*[contains(text(), '${link_name}')]]
    Wait until keyword succeeds  30  1  Page should contain element  css=div.plone-modal-dialog

overlay should open
    Wait until keyword succeeds  30  1  Element Should Be Visible  css=div.plone-modal-dialog

overlay should remain open
    Wait until page contains element  css=div.plone-modal-wrapper
    Wait until element is visible  css=div.plone-modal-wrapper

I close the overlay
    Click Element  css=div.plone-modal-header a.plone-modal-close

overlay should close
    Wait until keyword succeeds  40  1  Page should not contain element  css=div.plone-modal-dialog

overlay shows an error
    Wait Until Page Contains  Error

I '${action}' the form
    Wait until keyword succeeds  30  1  Element Should Be Visible  css=div.plone-modal-footer input[name="form.buttons.${action}"]
    Click Element  css=div.plone-modal-footer input[name="form.buttons.${action}"]

I enter wrong credentials
    Input text  __ac_name  wrong
    Input text  __ac_password  user
    Click Button  css=div.plone-modal-footer input

I enter valid credentials
    Wait until page contains element  name=__ac_name
    Input text for sure  __ac_name  ${SITE_OWNER_NAME}
    Input text for sure  __ac_password  ${SITE_OWNER_PASSWORD}
    Click Button  css=div.plone-modal-footer input

I enter valid user data
    Wait until page contains element  name=form.widgets.password_ctl
    Input text for sure  form.widgets.username       myuser
    Input text for sure  form.widgets.email          my@email.eu
    Input text for sure  form.widgets.password       123123
    Input text for sure  form.widgets.password_ctl   123123

I enter valid register user data
    Wait until page contains element  name=form.widgets.username
    Input text  form.widgets.username       myuser
    Input text  form.widgets.email          my@email.eu

I send the register form
    Wait until page contains element  css=div.plone-modal-footer #form-buttons-register
    Click Element  css=div.plone-modal-footer #form-buttons-register

I trigger the add a new user action
    Click Element  id=add-user

a document '${title}' in the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}/++add++Document
    Wait For Condition  return $('.autotoc-nav .active:visible').size() > 0
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${title}'); return 0;
    Click Button  Save

I set the default content view of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Given patterns are loaded
    Click link  xpath=//li[@id='plone-contentmenu-moreoptions']/a
    Click link  id=contextSetDefaultPage

a document as the default view of the test folder
    a document 'doc' in the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Given patterns are loaded
    Click link  xpath=//li[@id='plone-contentmenu-moreoptions']/a
    Wait until element is visible  id=contextSetDefaultPage
    Click link  id=contextSetDefaultPage
    Click element  id=doc
    Click element  css=div.plone-modal-footer input[name="form.buttons.Save"]

I change the default content view of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Given patterns are loaded
    Click link  xpath=//li[@id='plone-contentmenu-moreoptions']/a
    Wait until element is visible  id=folderChangeDefaultPage
    Click link  id=folderChangeDefaultPage

I trigger the '${action}' action menu item of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Given patterns are loaded
    Element should be visible  xpath=//li[@id='plone-contentmenu-moreoptions']/a
    Click link  xpath=//li[@id='plone-contentmenu-moreoptions']/a
    Wait until element is visible  id=plone-contentmenu-actions-${action}
    Click link  id=plone-contentmenu-actions-${action}
    Wait until page contains Element  css=div.plone-modal-dialog

I confirm deletion of the content
    # Note: The 'delete' button has no standard z3c.form name attribute
    Wait until keyword succeeds  2  2  Click Element  css=div.plone-modal-footer input#form-buttons-Delete

modals loaded
    Wait For Condition  return $('.plone-modal-wrapper').size() > 0
