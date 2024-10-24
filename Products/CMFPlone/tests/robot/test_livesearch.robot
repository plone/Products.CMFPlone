*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Variables    variables.py

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test cases ***


Scenario: Simple Livesearch
    Given a logged-in site administrator
      and a document    Welcome to Plone
     When I search for    Welcome
     Then the livesearch results should contain    Welcome to Plone
      and expected livesearch results    1

Scenario: Livesearch with image results
    Given a logged-in site administrator
      and a news item    My News with Image
     When I search for    My News
     Then the livesearch results should contain    My News with Image
      and expected livesearch results    1
      and Get Element Count    //*[contains(@class,"livesearch-results")]//li[contains(@class,"search-result")]//*[contains(@class,"col") and contains(@class,"img")]//img    greater than    0

     When I disable images in results in search controlpanel
      and I search for  My News
     and Get Element Count    //*[contains(@class,"livesearch-results")]//li[contains(@class,"search-result")]//*[contains(@class,"col") and contains(@class,"img")]//img    should be    0


*** Keywords ***

a document
    [Arguments]    ${title}
    Create content
    ...    type=Document
    ...    id=doc
    ...    title=${title}

a news item
    [Arguments]    ${title}
    Go to    ${PLONE_URL}/++add++News Item
    Type text    //input[@name="form.widgets.IDublinCore.title"]    ${title}
    Upload File By Selector    //input[@name="form.widgets.ILeadImageBehavior.image"]    ${PATH_TO_TEST_FILES}/pixel.png
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Item created    message=Image could not be created.

I search for
    [Arguments]    ${searchtext}
    Type Text    //input[@id="searchGadget"]    ${searchtext}

I search the currentfolder only for
    [Arguments]    ${searchtext}
    Check Checkbox    //*[@id="searchbox_currentfolder_only"]
    Type Text    //input[@id="searchGadget"]    ${searchtext}

the livesearch results should contain
    [Arguments]    ${text}
    Get Element States    //ul[contains(@class,"livesearch-results")]    contains    visible
    Get Text    //ul[contains(@class,"livesearch-results")]    contains    ${text}

the livesearch results should not contain
    [Arguments]    ${text}
    Get Element States    //ul[contains(@class,"livesearch-results")]    contains    visible
    Get Text    //ul[contains(@class,"livesearch-results")]    not contains    ${text}

expected livesearch results
    [Arguments]    ${num}
    Get Element Count    //*[contains(@class,"livesearch-results")]//li[contains(@class,"search-result")]    should be    ${num}


I disable images in results in search controlpanel
    Go to    ${PLONE_URL}/@@search-controlpanel
    Uncheck Checkbox    //input[@name="form.widgets.search_show_images:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved
