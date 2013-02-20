*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Variables  plone/app/testing/interfaces.py
Variables  Products/CMFPlone/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Variables ***

${TITLE} =  An actionsmenu page
${PAGE_ID} =  an-actionsmenu-page


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
      and i click outside of menu
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
     When i copy the page
      and i paste
     Then i should see 'Item(s) pasted.' in the page

*** Keywords ***

Suite Setup
    Open browser  ${PLONE_URL}  browser=${BROWSER}  remote_url=${REMOTE_URL}  desired_capabilities=${DESIRED_CAPABILITIES}
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}
    Go to  ${PLONE_URL}/createObject?type_name=Document
    Input text  name=title  ${TITLE}
    Click Button  Save

Suite Teardown
    Close All Browsers

Log in
    [Arguments]  ${userid}  ${password}
    Go to  ${PLONE_URL}/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

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

i click outside of menu
    Mouse Down  xpath=//h1

workflow link is clicked
    # store current state
    ${OLD_STATE} =  Get Text  xpath=//span[contains(@class,'state-')]
    Set Suite Variable  ${OLD_STATE}  ${OLD_STATE}
    Click Link  xpath=//dl[@id='plone-contentmenu-workflow']/dt/a
    Click Link  xpath=(//dl[@id='plone-contentmenu-workflow']/dd//a)[1]

state should have changed
    ${NEW_STATE} =  Get Text  xpath=//span[contains(@class,'state-')]
    Should Not Be Equal  ${NEW_STATE}  ${OLD_STATE}

Open Menu
    [Arguments]  ${elementId}
    Element Should Not Be Visible  css=dl#${elementId} dd.actionMenuContent
    Click link  css=dl#${elementId} dt.actionMenuHeader a
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=dl#${elementId} dd.actionMenuContent

Open Action Menu
    Open Menu  plone-contentmenu-actions

i copy the page
    Open Action Menu
    Click Link  link=Copy

i paste
    Open Action Menu
    Click Link  link=Paste

i should see '${message}' in the page
    Page Should Contain  ${message}