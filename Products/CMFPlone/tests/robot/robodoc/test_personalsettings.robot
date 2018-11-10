*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Test Cases ***

Show menubar
    Go to  ${PLONE_URL}

    Click link  css=#portal-personaltools a

    Wait until element is visible
    ...  css=#portal-personaltools li.plone-toolbar-submenu-header

    Mouse over  personaltools-preferences
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/show-preferences.png
    ...  css=div.plone-toolbar-container
    ...  css=li.plone-toolbar-submenu-header

Show personal preferences
    Go to  ${PLONE_URL}/@@personal-preferences

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/personal-preferences.png
    ...  css=#main-container

Show personal information
    Go to  ${PLONE_URL}/@@personal-information

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/personal-information.png
    ...  css=#main-container

Show changing password
    Go to  ${PLONE_URL}/@@change-password

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/change-password.png
    ...  css=#main-container