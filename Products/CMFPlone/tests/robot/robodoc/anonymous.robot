*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  Selenium2Screenshots/keywords.robot

Library  plone.app.robotframework.Zope2Server
Library  OperatingSystem

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Variables ***

${FIXTURE}  plone.app.robotframework.PLONE_ROBOT_TESTING
@{CONFIGURE_PACKAGES}
@{APPLY_PROFILES}  plone.app.contenttypes:plone-content
@{DIMENSIONS}  1024  768
${ROBOT_SERVER}  False

*** Keywords ***

Common Suite Setup
    Run keyword if  ${ROBOT_SERVER}  Setup Plone keywords
    Run keyword if  ${ROBOT_SERVER}  Remote ZODB setup  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  Setup Plone site  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  ZODB setup  ${FIXTURE}

    ${language} =  Get environment variable  LANGUAGE  'en'
    Set default language  ${language}

    Open test browser
    Run keyword and ignore error  Set window size  @{DIMENSIONS}

Common Suite Teardown
    Close all browsers
    Run keyword if  ${ROBOT_SERVER}  Remote ZODB TearDown  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  ZODB TearDown  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  Teardown Plone site

Setup Plone site
    [Arguments]  ${zope_layer_dotted_name}
    Start Zope server  ${zope_layer_dotted_name}
    Wait until keyword succeeds  2min  0s  Setup Plone keywords

Setup Plone keywords
    Import library  Remote  ${PLONE_URL}/RobotRemote

Teardown Plone site
    Close all browsers
    Stop Zope server

Highlight link
    [Arguments]  ${locator}
    Update element style  ${locator}  padding  0.5em
    Highlight  ${locator}


*** Test Cases ***

Take login link screenshot
    Go to  ${PLONE_URL}
    Highlight link  css=#personaltools-login
    Capture and crop page screenshot
    ...    ${CURDIR}/_robot/login-link.png
    ...    css=#content-header
    ...    css=#above-content-wrapper


Take login screenshot
    Go to  ${PLONE_URL}/login
    Capture and crop page screenshot
    ...    ${CURDIR}/_robot/login-popup.png
    ...    css=#content-core

Take annotated screenshot
    Go to  ${PLONE_URL}
    Highlight link  css=#personaltools-login
    Capture and crop page screenshot
    ...    ${CURDIR}/_robot/anonymous-surfing.png
    ...    css=#content-header
    ...    css=#above-content-wrapper

    Enable autologin as  Manager
    ${user_id} =  Translate  user_id
    ...  default=jane-doe
    ${user_fullname} =  Translate  user_fullname
    ...  default=Jane Doe
    Create user  ${user_id}  Member  fullname=${user_fullname}
    Set autologin username  ${user_id}

Take logged in screenshot
    Go to  ${PLONE_URL}
    Capture and crop page screenshot
    ...    ${CURDIR}/_robot/loggedin-surfing.png
    ...    css=#above-content-wrapper
    ...    css=div.plone-toolbar-container