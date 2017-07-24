*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Variables ***

@{DIMENSIONS}  1024  1200

*** Test Cases ***

Create sample content
    Go to  ${PLONE_URL}
    Capture page screenshot

    ${item} =  Create content  type=Folder
    ...  id=documentation  title=Documentation
    ...  description=Here you can find the documentation on our new product

Show state menu
    Go to  ${PLONE_URL}/documentation

    Click link  css=#plone-contentmenu-workflow a

    Wait until element is visible
    ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

    Mouse over  workflow-transition-advanced
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/workflow-advanced-menu.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

    Click link  workflow-transition-advanced
    Wait until element is visible
    ...   css=div.plone-modal-content

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/workflow-advanced.png
    ...  css=div.plone-modal-wrapper
