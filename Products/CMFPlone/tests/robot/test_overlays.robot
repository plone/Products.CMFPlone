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
    Given the 'Contact' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay opens
    Given the site root
     When I click the 'Log in' link
     Then overlay should open

Scenario: Log in form overlay closes
    Given the 'Log in' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay remains on wrong credentials
    Given the 'Log in' overlay
     When I enter wrong credentials
     Then overlay should remain open
      And overlay shows an error

# XXX: This test fails randomly on Jenkins.
#Scenario: Log in form overlay closes on valid credentials
#    Given the 'Log in' overlay
#     When I enter valid credentials
#     Then overlay should close

Scenario: Set default content item of a folder overlay opens
    Given a site owner
      And a document 'doc' in the test folder
     When I set the default content view of the test folder
     Then overlay should open

Scenario: Change default content item of a folder overlay opens
    Given a site owner
      And a document as the default view of the test folder
     When I change the default content view of the test folder
     Then overlay should open

Scenario: Change default content item of a folder overlay closes
    Given a site owner
      And a document as the default view of the test folder
     When I change the default content view of the test folder
      And I 'Cancel' the form
     Then overlay should close
     When I change the default content view of the test folder
      And I 'Save' the form
     Then overlay should close
     When I change the default content view of the test folder
      And I close the overlay
     Then overlay should close

Scenario: Delete content action overlay opens
    Given a site owner
     When I trigger the 'delete' action menu item of the test folder
     Then overlay should open

Scenario: Delete content action overlay closes
    Given a site owner
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
    Given a site owner
     When I trigger the 'rename' action menu item of the test folder
     Then overlay should open

Scenario: Rename content action overlay closes
    Given a site owner
     When I trigger the 'rename' action menu item of the test folder
      And I 'Cancel' the form
     Then overlay should close
     When I trigger the 'rename' action menu item of the test folder
      And I close the overlay
     Then overlay should close
     When I trigger the 'rename' action menu item of the test folder
      And I 'RenameAll' the form
     Then overlay should close

Scenario: Register user overlay opens
    Given the mail setup configured
      And the self registration enabled
      And the site root
     When I click the 'Register' link
     Then overlay should open

Scenario: Register user overlay closes
    Given the mail setup configured
      And the self registration enabled
      And the site root
      And the 'Register' overlay
     When I close the overlay
     Then overlay should close

Scenario: Register user overlay remains on wrong data
    Given the mail setup configured
      And the self registration enabled
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
    Given a site owner
      And the users and groups configlet
     When I trigger the add a new user action
     Then overlay should open

Scenario: New user overlay remains on wrong data
    Given a site owner
      And the users and groups configlet
      And I trigger the add a new user action
     When I send the register form
     Then overlay should remain open
      And overlay shows an error

Scenario: New user overlay closes on valid data
    Given a site owner
      And the users and groups configlet
      And I trigger the add a new user action
     When I enter valid user data
      And I send the register form
     Then overlay should close

Scenario: History overlay opens
    Given a site owner
      And the test folder
     When I click the 'History' link
     Then overlay should open

Scenario: History overlay closes
    Given a site owner
      And the test folder
      And the 'History' overlay
     When I close the overlay
     Then overlay should close

*** Keywords ***

Background
    Given a site owner
      and a test folder
    Disable autologin
    Go to homepage

the users and groups configlet
    Go to  ${PLONE_URL}/@@usergroup-userprefs

I click the '${link_name}' link
    Click Link  ${link_name}

the '${link_name}' overlay
    Click Link  ${link_name}
    Wait until keyword succeeds  30  1  Page should contain element  id=exposeMask

overlay should open
    Wait until keyword succeeds  30  1  Element Should Be Visible  id=exposeMask
    Element should be visible  css=div.overlay
    Element should be visible  css=div.overlay div.close

overlay should remain open
    Element should be visible  css=div.overlay

I close the overlay
    Click Element  css=div.overlay div.close

overlay should close
    Element should not remain visible  id=exposeMask
    Wait until keyword succeeds  30  1  Page should not contain element  css=div.overlay

overlay shows an error
    Wait Until Page Contains  Error

I '${action}' the form
    Wait until keyword succeeds  30  1  Element Should Be Visible  id=exposeMask
    Click Element  name=form.button.${action}

I enter wrong credentials
    Input text  __ac_name  wrong
    Input text  __ac_password  user
    Click Button  Log in

I enter valid credentials
    Wait until page contains element  name=__ac_name
    Input text for sure  __ac_name  ${SITE_OWNER_NAME}
    Input text for sure  __ac_password  ${SITE_OWNER_PASSWORD}
    Click Button  Log in

I enter valid user data
    Wait until page contains element  name=form.username
    Input text for sure  form.username       myuser
    Input text for sure  form.email          my@email.eu
    Input text for sure  form.password       123123
    Input text for sure  form.password_ctl   123123

I enter valid register user data
    Wait until page contains element  name=form.username
    Input text  form.username       myuser
    Input text  form.email          my@email.eu

I send the register form
    Wait until page contains element  name=form.actions.register
    Click Element  name=form.actions.register

I trigger the add a new user action
    Click Element  name=users_add

a document '${title}' in the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Document
    Input text  name=title  ${title}
    Click Button  Save

I set the default content view of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Click link  xpath=//dl[@id='plone-contentmenu-display']/dt/a
    Click link  id=contextSetDefaultPage

a document as the default view of the test folder
    a document 'doc' in the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}/select_default_page?form.submitted=1&objectId=doc

I change the default content view of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Click link  xpath=//dl[@id='plone-contentmenu-display']/dt/a
    Click link  id=folderChangeDefaultPage

I trigger the '${action}' action menu item of the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}
    Click link  xpath=//dl[@id='plone-contentmenu-actions']/dt/a
    Click link  id=plone-contentmenu-actions-${action}
    Wait until page contains Element  id=exposeMask

I confirm deletion of the content
    # Note: The 'delete' button has no standard z3c.form name attribute
    Wait until keyword succeeds  2  2  Click Element  xpath=//form[@id='delete_confirmation']//input[@class='destructive']
