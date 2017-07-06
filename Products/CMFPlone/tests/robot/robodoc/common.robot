*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  Selenium2Screenshots/keywords.robot

Library  plone.app.robotframework.Zope2Server
Library  OperatingSystem

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

    Enable autologin as  Manager
    ${user_id} =  Translate  user_id
    ...  default=jane-doe
    ${user_fullname} =  Translate  user_fullname
    ...  default=Jane Doe
    Create user  ${user_id}  Member  fullname=${user_fullname}
    Set autologin username  ${user_id}

    Open test browser
    Run keyword and ignore error  Set window size  @{DIMENSIONS}

Common Suite Teardown
    Close all browsers
    Run keyword if  ${ROBOT_SERVER}  Remote ZODB TearDown  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  ZODB TearDown  ${FIXTURE}
    Run keyword if  not ${ROBOT_SERVER}  Teardown Plone site

Setup Plone site
    [Arguments]  ${zope_layer_dotted_name}  @{extra_layers_dotted_names}

    Start Zope server  ${zope_layer_dotted_name}
    :FOR  ${extra_layer_dotted_name}  IN  @{extra_layers_dotted_names}
    \     Amend Zope server  ${extra_layer_dotted_name}
    Set Zope layer  ${zope_layer_dotted_name}

    Wait until keyword succeeds  2min  0s  Setup Plone keywords

Setup Plone keywords
    Import library  Remote  ${PLONE_URL}/RobotRemote

Teardown Plone site
    Close all browsers
    Stop Zope server
