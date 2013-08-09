*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Run keywords  Open SauceLabs test browser  Background
Test Teardown  Run keywords  Report test status  Close all browsers

*** Variables ***

${TITLE}  An actionsmenu page
${PAGE_ID}  an-actionsmenu-page

*** Test cases ***

# ---
# Basic Contentactions menu
# ---

Scenario: Actions Menu rendered collapsed
    Given an actionsmenu page
     Then delete link exists
      and delete link should not be visible

Scenario: Clicking expands action menu
    Given an actionsmenu page
     When menu link is clicked
     Then actions menu should be visible

Scenario: Clicking again collapses action menu
    Given an actionsmenu page
     When menu link is clicked
      and menu link is clicked

# ---
# Switching Contentactions menu by MouseOver
# ---

Scenario: Hovering mouse from expanded menu on other menu shows that menu
    Given an actionsmenu page
     When first menu link is clicked
      and mouse moves to second menu
     Then second menu should be visible
      and first menu should not be visible

# ---
# Clicking outside of Contentactions menu
# ---

Scenario: Clicking outside of Contentactions menu
    Given an actionsmenu page
     When first menu link is clicked
      and I click outside of menu
     Then first menu should not be visible

# ---
# Workflow stuff
# ---

Scenario: Do a workflow change
    Given an actionsmenu page
     When workflow link is clicked
     Then state should have changed

# ---
# Copy stuff
# ---

Scenario:
    Given an actionsmenu page
     When I copy the page
      and I paste
     Then I should see 'Item(s) pasted.' in the page

*** Keywords ***

Background
    Given a site owner
      and a test document

a test document
    Go to  ${PLONE_URL}/createObject?type_name=Document
    Input text  name=title  ${TITLE}
    Click Button  Save

an actionsmenu page
    Go to  ${PLONE_URL}/${PAGE_ID}

delete link exists
     Page Should Contain Element  xpath=//div[@class='contentActions']//a[@id='plone-contentmenu-actions-delete']

delete link should not be visible
     Element Should Not Be Visible  xpath=//div[@class='contentActions']//a[@id='plone-contentmenu-actions-delete']

menu link is clicked
    Click Link  css=dl#plone-contentmenu-actions dt.actionMenuHeader a

delete link should be visible
    Element Should Be Visible  xpath=//div[@class='contentActions']//a[@id='plone-contentmenu-actions-delete']

actions menu should be visible
    Element Should Be Visible  xpath=//dl[@id='plone-contentmenu-actions']/dd

first menu link is clicked
    Click Link  xpath=(//div[@class="contentActions"]//dt[contains(@class, 'actionMenuHeader')]/a)[1]

mouse moves to second menu
    Click Link  xpath=(//div[@class="contentActions"]//dt[contains(@class, 'actionMenuHeader')]/a)[2]

second menu should be visible
    Element Should Be Visible  xpath=(//dl[contains(@class, 'actionMenu')])[2]

first menu should not be visible
    Wait until keyword succeeds  10s  1s  Element Should Not Be Visible  xpath=(//dl[contains(@class, 'actionMenu')])[1]//dd

I click outside of menu
    Click Element  xpath=//h1

workflow link is clicked
    # store current state
    ${OLD_STATE} =  Get Text  xpath=//span[contains(@class,'state-')]
    Set Suite Variable  ${OLD_STATE}  ${OLD_STATE}
    Click Link  xpath=//dl[@id='plone-contentmenu-workflow']/dt/a
    Click Link  xpath=(//dl[@id='plone-contentmenu-workflow']/dd//a)[1]
    # FIXME: The above 'Click Link' fails on Internet Explorer, but the
    # following keywords 'workflow link is clicked softly' passes. Until we
    # know why, we check if the above worked and if not, we try the other
    # approach.
    @{value} =  Run Keyword And Ignore Error
    ...         Page Should Contain  Item state changed.
    Run Keyword If  '@{value}[0]' == 'FAIL'
    ...         workflow link is clicked softly

workflow link is clicked softly
    [Documentation]  This works on Internet Explorer, but not on Firefox...
    Mouse Over  xpath=//dl[@id='plone-contentmenu-workflow']/dt/a
    Click Link  xpath=//dl[@id='plone-contentmenu-workflow']/dt/a
    Mouse Over  xpath=(//dl[@id='plone-contentmenu-workflow']/dd//a)[1]
    Mouse Down  xpath=(//dl[@id='plone-contentmenu-workflow']/dd//a)[1]
    Mouse Up  xpath=(//dl[@id='plone-contentmenu-workflow']/dd//a)[1]
    Wait until page contains  Item state changed.

state should have changed
    Wait until page contains  Item state changed
    ${NEW_STATE} =  Get Text  xpath=//span[contains(@class,'state-')]
    Should Not Be Equal  ${NEW_STATE}  ${OLD_STATE}

Open Menu
    [Arguments]  ${elementId}
    Element Should Not Be Visible  css=dl#${elementId} dd.actionMenuContent
    Click link  css=dl#${elementId} dt.actionMenuHeader a
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=dl#${elementId} dd.actionMenuContent

Open Action Menu
    Open Menu  plone-contentmenu-actions

I copy the page
    Open Action Menu
    Click Link  link=Copy
    Page should contain  copied

I paste
    Go to  ${PLONE_URL}
    Open Action Menu
    Click Link  link=Paste

I should see '${message}' in the page
    Wait until page contains  ${message}
    Page should contain  ${message}
