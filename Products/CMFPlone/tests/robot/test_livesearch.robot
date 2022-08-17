*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Variables  Products/CMFPlone/tests/robot/variables.py

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test cases ***************************************************************


Scenario: Simple Livesearch
    Given a logged-in site administrator
      and a document  Welcome to Plone
     When I search for  Welcome
     Then the livesearch results should contain  Welcome to Plone
      and expected livesearch results  1

Scenario: Livesearch with image results
    Given a logged-in site administrator
      and a news item  My News with Image
     When I search for  My News
     Then the livesearch results should contain  My News with Image
      and expected livesearch results  1
      and Page should contain image  css=.livesearch-results li.search-result .col.img img

     When I disable images in results in search controlpanel
      and I search for  My News
     Then Page should not contain image  css=.livesearch-results li.search-result .col.img img


*** Keywords *****************************************************************

a document
    [Arguments]  ${title}
    Create content  type=Document  id=doc  title=${title}

a news item
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/++add++News Item
    Wait until page contains  Add News Item
    Input text  name=form.widgets.IDublinCore.title  ${title}
    Choose File  name=form.widgets.ILeadImageBehavior.image  ${PATH_TO_TEST_FILES}/plone-logo.png
    Click Button  Save
    Wait until page contains  Item created  error=Image could not be created.

I search for
    [Arguments]  ${searchtext}
    Input text  css=input#searchGadget  ${searchtext}
    Wait For Element  css=input#searchGadget

I search the currentfolder only for
    [Arguments]  ${searchtext}
    Select checkbox  id=searchbox_currentfolder_only
    Input text  css=input#searchGadget  ${searchtext}
    Wait For Element  css=input#searchGadget

the livesearch results should contain
    [Arguments]  ${text}
    Wait until keyword succeeds  5s  1s  Element should contain  css=.livesearch-results li a .heading  ${text}

the livesearch results should not contain
    [Arguments]  ${text}
    Wait until keyword succeeds  5s  1s  Page should not contain  css=.livesearch-results li a .heading  ${text}

expected livesearch results
    [Arguments]  ${num}
    ${count} =  Get Element Count  css=.livesearch-results li.search-result
    Should Be Equal as Numbers  ${count}  ${num}

I disable images in results in search controlpanel
    Go to  ${PLONE_URL}/@@search-controlpanel
    Wait until page contains  Search Settings
    Unselect Checkbox  form.widgets.search_show_images:list
    Click Button  Save
    Wait until page contains  Changes saved
