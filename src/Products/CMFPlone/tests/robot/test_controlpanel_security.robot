*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

*** Test Cases ***

Scenario: Enable self registration in the Security Control Panel
    Given a logged-in site administrator
      and the security control panel
     When I enable self registration
     Then anonymous users can register to the site

Scenario: Enable users to select their own passwords in the Security Control Panel
    Given a logged-in site administrator
      and the security control panel
     When I enable users to select their own passwords
     Then users can select their own passwords when registering

Scenario: Enable user folders in the Security Control Panel
    Given a logged-in site administrator
      and the security control panel
     When I enable user folders
     Then a user folder should be created when a user registers and logs in to the site

Scenario: Enable anyone to view 'about' information in the Security Control Panel
    Given a logged-in site administrator
      and a published test folder
      and the security control panel
     When I enable anyone to view 'about' information
     Then anonymous users can view 'about' information

Scenario: Enable use email as login in the Security Control Panel
    Given a logged-in site administrator
      and the security control panel
     When I enable email to be used as a login name
     Then users can use email as their login name

Scenario: Enable use uuid as uid in the Security Control Panel
    Given a logged-in site administrator
      and the security control panel
     When I enable UUID to be used as a user id
     Then UUID should be used for the user id


*** Keywords ***

# GIVEN

the security control panel
    Go to    ${PLONE_URL}/@@security-controlpanel
    Get Text    //body    contains    Security Settings

a published test folder
    Go to    ${PLONE_URL}/test-folder
    Click    //li[@id="plone-contentmenu-workflow"]/a
    Click    //*[@id="workflow-transition-publish"]
    Get Text    //body    contains    Item state changed

# WHEN

I enable self registration
    Check Checkbox  //input[@name="form.widgets.enable_self_reg:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable users to select their own passwords
    Check Checkbox    //input[@name="form.widgets.enable_self_reg:list"]
    Check Checkbox    //input[@name="form.widgets.enable_user_pwd_choice:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable user folders
    Check Checkbox    //input[@name="form.widgets.enable_self_reg:list"]
    Check Checkbox    //input[@name="form.widgets.enable_user_pwd_choice:list"]
    Check Checkbox    //input[@name="form.widgets.enable_user_folders:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable anyone to view 'about' information
    Check Checkbox    //input[@name="form.widgets.allow_anon_views_about:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable email to be used as a login name
    Check Checkbox    //input[@name="form.widgets.enable_self_reg:list"]
    Check Checkbox    //input[@name="form.widgets.enable_user_pwd_choice:list"]
    Check Checkbox    //input[@name="form.widgets.use_email_as_login:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable UUID to be used as a user id
    Check Checkbox    //input[@name="form.widgets.enable_self_reg:list"]
    Check Checkbox    //input[@name="form.widgets.enable_user_pwd_choice:list"]
    Check Checkbox    //input[@name="form.widgets.use_uuid_as_userid:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


# THEN

Anonymous users can register to the site
    Disable autologin
    Go to    ${PLONE_URL}
    Get Text    //body    contains    Plone site
    Get Element States    //a[@id="personaltools-join"]    contains    visible

Users can select their own passwords when registering
    Disable autologin
    Go to    ${PLONE_URL}/@@register
    Get Text    //body    contains    Registration form
    Get Element States    //input[@id="form-widgets-password"]    contains    visible

Users can use email as their login name
    Disable autologin
    Go to    ${PLONE_URL}/@@register
    Get Text    //body    contains    Registration form
    Get Element States    //input[@id="form-widgets-email"]    contains    visible
    Get Element States    //input[@id="form-widgets-username"]    not contains    visible

A user folder should be created when a user registers and logs in to the site

    Disable autologin
    I register to the site
    I login to the site
    # The user folder should be created
    Go to    ${PLONE_URL}/Members/joe
    Get Element Count    //h1[contains(text(),'joe doe')]    should be    1
    Get Text    //body    not contains    This page does not seem to exist

Anonymous users can view 'about' information
    Disable autologin
    Go to    ${PLONE_URL}/@@search?SearchableText=test
    Get Text    //body    contains    Search results
    Get Element States    //span[contains(@class, 'documentAuthor')]    contains    visible

UUID should be used for the user id

    Disable autologin
    I register to the site
    I login to the site
    # XXX: Here we can't really test that this is a uuid, since it's random, so
    # we just check that user id is not equal to username or email
    ${userid}=  Get Text    //a[@id='personaltools-menulink']
    Should Not Be Equal As Strings    ${userid}    joe
    Should Not Be Equal As Strings    ${userid}    joe@test.com


# DRY

I register to the site
    Go to  ${PLONE_URL}/@@register
    Get Text    //body    contains    Registration form
    Type Text    //input[@name="form.widgets.fullname"]    joe doe
    Type Text    //input[@name="form.widgets.username"]    joe
    Type Text    //input[@name="form.widgets.email"]    joe@test.com
    Type Text    //input[@name="form.widgets.password"]    supersecret
    Type Text    //input[@name="form.widgets.password_ctl"]    supersecret
    Click    //button[@name="form.buttons.register"]

I login to the site
    Go to    ${PLONE_URL}/login
    Get Text    //body    contains    Login Name
    Type Text    //input[@name="__ac_name"]    joe
    Type Text    //input[@name="__ac_password"]    supersecret
    Click    //button[@name="buttons.login"]
    Get Text    //body    contains    You are now logged in