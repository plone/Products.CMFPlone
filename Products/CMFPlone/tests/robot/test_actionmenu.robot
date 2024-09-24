*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot


Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

*** Variables ***

${TITLE}    An actionsmenu page
${PAGE_ID}    an-actionsmenu-page


*** Test Cases ***

# ---
# Basic Contentactions menu
# ---

Scenario: Actions Menu rendered collapsed
    Given a logged-in site administrator
      and an actionsmenu page
     Then delete link exists
      and delete link should not be visible

Scenario: Clicking expands action menu
    Given a logged-in site administrator
      and an actionsmenu page
     When menu link is clicked
     Then actions menu should be visible

Scenario: Clicking again collapses action menu
    Given a logged-in site administrator
      and an actionsmenu page
     When menu link is clicked
      and menu link is clicked
     Then actions menu should not be visible

# ---
# Switching Contentactions menu by MouseOver
# ---

Scenario: Click from expanded menu on other menu shows that menu
    Given a logged-in site administrator
      and an actionsmenu page
     When first menu link is clicked
      and mouse moves to second menu
     Then second menu should be visible
      and first menu should not be visible

# ---
# Clicking outside of Contentactions menu
# ---

Scenario: Clicking outside of Contentactions menu
    Given a logged-in site administrator
      and an actionsmenu page
     When menu link is clicked
      and I click outside of menu
     Then actions menu should not be visible

# ---
# Workflow stuff
# ---

Scenario: Do a workflow change
    Given a logged-in site administrator
      and an actionsmenu page
     When workflow link is clicked
     Then state should have changed

# ---
# Copy stuff
# ---

Scenario:
    Given a logged-in site administrator
      and an actionsmenu page
     When I copy the page
      and I paste
     Then I should see 'Item(s) pasted.' in the page


*** Keywords ***

# GIVEN

an actionsmenu page
    Create content    type=Document    title=${TITLE}
    Go To    ${PLONE_URL}/${PAGE_ID}
    Get Text    //body    contains    An actionsmenu page

# WHEN

first menu link is clicked
    Click    xpath=//li[@id='plone-contentmenu-workflow']/a

mouse moves to second menu
    Click    xpath=//li[@id='plone-contentmenu-actions']/a

I click outside of menu
    Click    xpath=//h1

workflow link is clicked
    # store current state
    ${OLD_STATE}=    Get Text    xpath=(//span[contains(@class,'state-')])
    Set Suite Variable    ${OLD_STATE}    ${OLD_STATE}
    Click    xpath=//li[@id='plone-contentmenu-workflow']/a
    Click    xpath=(//li[@id='plone-contentmenu-workflow']/ul/li/a)[1]
    Get Text    //body    contains    Item state changed.

I copy the page
    Open Action Menu
    Click    xpath=//li[@id='plone-contentmenu-actions']//a[contains(@class,'actionicon-object_buttons-copy')]
    Get Text    //body    contains    copied

I paste
    Go to  ${PLONE_URL}
    Open Action Menu
    Click    xpath=//li[@id='plone-contentmenu-actions']//a[contains(@class,'actionicon-object_buttons-paste')]


# THEN

delete link exists
    Get Element Count    xpath=//a[@id='plone-contentmenu-actions-delete']    should be    1

delete link should not be visible
    Wait For Elements State    xpath=//li[@id='plone-contentmenu-actions']/a[@id='plone-contentmenu-actions-delete']    hidden

menu link is clicked
    Click    xpath=//li[@id='plone-contentmenu-actions']/a

second menu should be visible
    Get Element States    xpath=//li[@id='plone-contentmenu-actions']/ul[contains(@class,'dropdown-menu')]    contains    visible

first menu should not be visible
    Get Element States    xpath=//li[@id='plone-contentmenu-workflow']/ul[contains(@class,'dropdown-menu')]    contains    hidden

actions menu should not be visible
    Get Element States    xpath=//li[@id='plone-contentmenu-actions']/ul[contains(@class,'dropdown-menu')]    contains    hidden

actions menu should be visible
    Get Element States    xpath=//li[@id='plone-contentmenu-actions']/ul[contains(@class,'dropdown-menu')]    contains    visible

state should have changed
    ${NEW_STATE}=    Get Text    xpath=(//span[contains(@class,'state-')])
    Should Not Be Equal As Strings    ${NEW_STATE}    ${OLD_STATE}

I should see '${message}' in the page
    Get Text    //body    contains    ${message}


# DRY

Open Action Menu
    Click    xpath=//li[@id='plone-contentmenu-actions']/a
    actions menu should be visible
