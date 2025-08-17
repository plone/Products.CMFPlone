*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Variables    variables.py

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

*** Variables ***

${TEST_FOLDER}  test-folder

*** Test cases ***

Scenario: Contact form overlay opens
    Given the site root
     When I click the 'Contact' link
     Then overlay should open


Scenario: Contact form overlay closes
    Given the site root logged out
      and the 'Contact' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay opens
    Given the site root logged out
      and the site root
     When I click the 'Log in' link
     Then overlay should open

Scenario: Log in form overlay closes
    Given the site root logged out
      and the site root
      and the 'Log in' overlay
     When I close the overlay
     Then overlay should close

Scenario: Log in form overlay remains on wrong credentials
    Given the site root logged out
      and the site root
      and the 'Log in' overlay
     When I enter wrong credentials
     Then overlay should remain open
      and login overlay shows an error

Scenario: Log in form overlay closes on valid credentials
    Given the site root logged out
      and the site root
      and the 'Log in' overlay
     When I enter valid credentials
     Then overlay should close

Scenario: Set default content item of a folder overlay opens
    Given a logged-in site administrator
      and a document 'doc' in the test folder
     When I set the default content view of the test folder
     Then overlay should open

Scenario: Change default content item of a folder overlay opens
   Given a logged-in site administrator
     and a document as the default view of the test folder
    When I change the default content view of the test folder
    Then overlay should open

Scenario: Change default content item of a folder overlay closes
   Given a logged-in site administrator
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
      and the site root logged out
      And the site root
     When I click the 'Register' link
     Then overlay should open

Scenario: Register user overlay closes
    Given the mail setup configured
      And the self registration enabled
      and the site root logged out
      And the site root
      And the 'Register' overlay
     When I close the overlay
     Then overlay should close

Scenario: Register user overlay remains on wrong data
    Given the mail setup configured
      And the self registration enabled
      and the site root logged out
      And the site root
      And the 'Register' overlay
     When I send the register form
     Then overlay should remain open
      And overlay shows an error

# Tests based on MockupMailServer, this should be a valid tests
Scenario: Register user overlay closes on valid data
   Given the mail setup configured
     And the self registration enabled
     And the site root
     And the 'Register' overlay
    When I enter valid register user data
     And I send the register form
    Then overlay should close

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
      And overlay requires to compile a field

Scenario: New user overlay closes on valid data
    Given a logged-in site administrator
      And the users and groups configlet
      And I trigger the add a new user action
     When I enter valid user data
      And I send the register form
     Then overlay should close


*** Keywords ***

# GIVEN
the site root logged out
    Go to    ${PLONE_URL}/logout

the site root
    Go to    ${PLONE_URL}


the '${link_name}' overlay
    Click    //a[descendant-or-self::*[contains(text(), "${link_name}")]]
    Get Element Count    //div[contains(@class,"modal-dialog")]    greater than    0


a document '${title}' in the test folder
    Go to    ${PLONE_URL}/${TEST_FOLDER}/++add++Document
    Type Text    //input[@id="form-widgets-IDublinCore-title"]    ${title}
    Click    //button[@name="form.buttons.save"]


a document as the default view of the test folder
    a document 'doc' in the test folder
    Go to    ${PLONE_URL}/${TEST_FOLDER}
    Click    //li[@id='plone-contentmenu-display']/a
    Click    //a[@id="contextSetDefaultPage"]
    Click    //input[@id="doc"]
    Click    //div[contains(@class,"modal-footer")]//button[@name="form.buttons.Save"]
    Wait For Condition    Text    //body//h1    contains    doc


the users and groups configlet
    Go to    ${PLONE_URL}/@@usergroup-userprefs
    Get Text    //body    contains    User Search

# WHEN

I click the '${link_name}' link
    Get Element Count    //a[descendant-or-self::*[contains(text(), "${link_name}")]]    greater than    0
    Click    //a[descendant-or-self::*[contains(text(), "${link_name}")]]


I close the overlay
    Click    //div[contains(@class,"modal-header")]//button[contains(@class,"modal-close")]


I enter wrong credentials
    I enter credentials    wrong    user


I enter valid credentials
    I enter credentials    ${SITE_OWNER_NAME}    ${SITE_OWNER_PASSWORD}


I set the default content view of the test folder
    Go to    ${PLONE_URL}/${TEST_FOLDER}
    Click    //li[@id='plone-contentmenu-display']/a
    Click    //a[@id="contextSetDefaultPage"]


I change the default content view of the test folder
    Go to    ${PLONE_URL}/${TEST_FOLDER}
    Click    //li[@id='plone-contentmenu-display']/a
    Click    //a[@id="folderChangeDefaultPage"]


I '${action}' the form
    Click    //div[contains(@class,"modal-footer")]//button[@name="form.buttons.${action}"]


I trigger the '${action}' action menu item of the test folder
    Go to    ${PLONE_URL}/${TEST_FOLDER}
    Click    //li[@id="plone-contentmenu-actions"]/a
    Click    //a[@id="plone-contentmenu-actions-${action}"]


I confirm deletion of the content
    Click    //div[contains(@class,"modal-footer")]//button[@name="form.buttons.Delete"]


I send the register form
    Click    //div[contains(@class,"modal-footer")]//button[@name="form.buttons.register"]


I enter valid register user data
    Type Text    //input[@name="form.widgets.username"]    myuser
    Type Text    //input[@name="form.widgets.email"]    myuser@plone.org


I trigger the add a new user action
    Click    //a[@id="add-user"]


I enter valid user data
    Type Text    //input[@name="form.widgets.username"]    myuser
    Type Text    //input[@name="form.widgets.email"]    myuser@plone.org
    Type Text    //input[@name="form.widgets.password"]    newpassword
    Type Text    //input[@name="form.widgets.password_ctl"]    newpassword



# THEN

overlay should open
    Wait For Condition    Element States    //div[contains(@class,"modal-dialog")]    contains    visible


overlay should close
    Wait For Condition    Element Count    //div[contains(@class,"modal-dialog")]    should be    0


overlay should remain open
    Wait For Condition    Element States    //div[contains(@class,"modal-wrapper")]    contains    visible


login overlay shows an error
    Wait For Condition    Text    //div[contains(@class,"modal-wrapper")]    contains    Error


overlay shows an error
    Wait For Condition    Text    //div[contains(@class,"modal-wrapper")]    contains    There were errors


overlay requires to compile a field
    Wait For Condition    Text    //div[contains(@class,"modal-wrapper")]    contains    Required input is missing


# DRY
I enter credentials
    [Arguments]    ${username}    ${password}
    Type Text    //input[@name="__ac_name"]    ${username}
    Type Text    //input[@name="__ac_password"]    ${password}
    Click    //div[contains(@class,"modal-footer")]//button
