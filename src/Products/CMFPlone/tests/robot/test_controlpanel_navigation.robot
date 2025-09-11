*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Disable Generate Tabs in the Navigation Control Panel
    Given a logged-in site administrator
      and a document 'My Document'
      and the navigation control panel
     When I disable generate tabs
     Then the document 'My Document' does not show up in the navigation

Scenario: Enable Folderish Tabs in the Navigation Control Panel
    Given a logged-in site administrator
      and a document 'My Document'
      and the navigation control panel
     When I disable non-folderish tabs
     Then the document 'My Document' does not show up in the navigation

Scenario: Filter Navigation By Displayed Types in the Navigation Control Panel
    Given a logged-in site administrator
      and a document 'My Document'
      and the navigation control panel
     When I remove 'Document' from the displayed types list
     Then the document 'My Document' does not show up in the navigation
      and the document 'My Document' does not show up in the sitemap

Scenario: Filter Navigation By Workflow States in the Navigation Control Panel
    Given a logged-in site administrator
      and a published document 'My Document'
      and a private document 'My Internal Document'
      and the navigation control panel
     When I enable filtering by workflow states
      and I choose to show 'published' items
      and I choose to not show 'private' items
     Then the document 'My Document' shows up in the navigation
      and the document 'My Internal Document' does not show up in the navigation


*** Keywords ***

# GIVEN

the navigation control panel
    Go to  ${PLONE_URL}/@@navigation-controlpanel
    Get Text    //body    contains    Navigation Settings

a published document '${title}'
    ${uid}=    Create content
    ...    type=Document
    ...    id=doc
    ...    title=${title}
    Fire transition    ${uid}    publish

a private document '${title}'
    Create content
    ...    type=Document
    ...    id=doc1
    ...    title=${title}


# WHEN

I disable generate tabs
    Uncheck Checkbox    //input[@name="form.widgets.generate_tabs:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

I disable non-folderish tabs
    Uncheck Checkbox  //input[@value='Document']
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

I remove '${portal_type}' from the displayed types list
    Uncheck Checkbox  //input[@value='Document']
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

I enable filtering by workflow states
    Check Checkbox    //input[@name="form.widgets.filter_on_workflow:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

I choose to show '${workflow_state}' items
    Check Checkbox    //input[@value='${workflow_state}']
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

I choose to not show '${workflow_state}' items
    Uncheck Checkbox    //input[@value='${workflow_state}']
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.


# THEN

the document '${title}' shows up in the navigation
    Go to    ${PLONE_URL}
    Get Element Count    //ul[@id='portal-globalnav']/li/a[contains(text(), '${title}')]    should be    1    message=The global navigation should have contained the item '${title}'

the document '${title}' does not show up in the navigation
    Go to    ${PLONE_URL}
    Get Element Count    //ul[@id='portal-globalnav']/li/a[contains(text(), '${title}')]    should be    0    message=The global navigation should not have contained the item '${title}'

the document '${title}' does not show up in the sitemap
    Go to    ${PLONE_URL}/sitemap
    Get Element Count    //ul[@id='portal-sitemap']/li/a/span[contains(text(), '${title}')]    should be    0    message=The sitemap should not have contained the item '${title}'
