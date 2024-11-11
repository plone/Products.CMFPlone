*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Enable Livesearch in the Search Control Panel
    Given a logged-in site administrator
      and a document 'My Document'
      and the search control panel
     When I enable livesearch
     Then then searching for 'My Document' will show a live search

Scenario: Exclude Content Types from Search
    Given a logged-in site administrator
      and a document 'My Document'
      and the search control panel
     When I exclude the 'Document' type from search
     Then searching for 'My Document' will not return any results


*** Keywords ***

# GIVEN

the search control panel
    Go to    ${PLONE_URL}/@@search-controlpanel
    Get Text    //body    contains    Search Settings

# WHEN

I enable livesearch
    Check Checkbox  //input[@name="form.widgets.enable_livesearch:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I exclude the '${portal_type}' type from search
    # Make sure we see the checkbox, in expanded in jenkins it gets a bit under the toolbar
    Check Checkbox  //input[@name='form.widgets.types_not_searched:list' and @value='${portal_type}']
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


# THEN

then searching for 'My Document' will show a live search
    Go to    ${PLONE_URL}
    Type Text    //input[@name="SearchableText"]    My D
    Get Element States    //ul[contains(@class,"livesearch-results")]    contains    visible
    Get Text    //ul[contains(@class,"livesearch-results")]    contains    My Document

searching for '${search_term}' will not return any results
    Go to    ${PLONE_URL}/@@search
    Get Text    //body    contains    No results were found
    Type Text    //form[@id='searchform']//input[@name='SearchableText']    ${search_term}
    Click    //input[@type="submit" and @value="Search"]
    Get Text    //body    contains    items matching your search terms
    Get Text    //span[@id='search-results-number']    should be    0
