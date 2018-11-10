*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Variables ***

@{DIMENSIONS}  1280  1600

*** Test Cases ***

Create sample content
    Go to  ${PLONE_URL}

    ${item} =  Create content  type=Document
    ...  id=samplepage  title=Sample Page
    ...  description=The long wait is now over
    ...  text=<p>Our new site is built with Plone.</p>


Show state menu
    Go to  ${PLONE_URL}/samplepage

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-workflow
    Click element  css=span.icon-plone-contentmenu-workflow

    Wait until element is visible
    ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

    Mouse over  workflow-transition-publish
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/workflow-basic.png
            ...  css=#content-header
            ...  css=div.plone-toolbar-container

Show sendback
    Go to  ${PLONE_URL}/samplepage

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-workflow
    Click element  css=span.icon-plone-contentmenu-workflow

    Wait until element is visible
    ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

    click link  workflow-transition-submit

    Go to  ${PLONE_URL}/samplepage

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-workflow
    Click element  css=span.icon-plone-contentmenu-workflow

    Wait until element is visible
    ...  css=#plone-contentmenu-workflow li.plone-toolbar-submenu-header

    Mouse over  workflow-transition-reject
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/workflow-reject.png
            ...  css=#content-header
            ...  css=div.plone-toolbar-container

Create sample folder
    Go to  ${PLONE_URL}

    ${item} =  Create content  type=Folder
    ...  id=documentation  title=Documentation
    ...  description=Here you can find the documentation on our new product

Show sharing menu

    Go to  ${PLONE_URL}/documentation

    Click link  css=#contentview-local_roles a

    Wait until element is visible
    ...  css=#user-group-sharing-container

    Update element style  portal-footer  display  none


    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/sharing-menu.png
            ...  css=#content-header
            ...  css=div.plone-toolbar-container