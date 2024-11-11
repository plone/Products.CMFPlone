*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Variables    variables.py

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Location query Current
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the operator Current in the criteria Location
     Then we expect 1 hits

Scenario: Location query Parent
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the operator Parent in the criteria Location
     Then we expect 3 hits

Scenario: Location query Custom
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the operator Custom in the criteria Location
      and I search in B subfolder in the related item widget
     Then we expect 5 hits

Scenario: Location query Advanced
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the operator Advanced in the criteria Location
     Then I expect to be in Advanced mode

Scenario: Location query Simple
    # this fails simple is not available, first select 'Advanced Mode' then you can select 'Simple Mode'
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the operator Advanced in the criteria Location
      and I open the select box titled operator
      and I select index Simple
     Then I expect to be in Simple mode

Scenario: Title query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I open the criteria Title
      and I search for A
     Then we expect 1 hits

Scenario: Description query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I open the criteria Description
      and I search for a
     Then we expect 1 hits

Scenario: Searchable text query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I open the criteria Searchable text
      and I search for a
      and Sleep  0.2
     Then we expect 2 hits

     When I open the criteria Searchable text
      and I search for d
     Then we expect 1 hits

Scenario: Tag query one

    ${base_option_selector}=    Set Variable    select2-results-dept-0 select2-result select2-result-selectable select2-option
    ${base_option_selector_o}=    Set Variable    ${base_option_selector}-o
    ${base_option_selector_n}=    Set Variable    ${base_option_selector}-n
    ${base_option_selector_p}=    Set Variable    ${base_option_selector}-p
    ${base_option_selector_e}=    Set Variable    ${base_option_selector}-e
    # tests the "Matches any of" option
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the default operator in the criteria Tag
      and I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_o}")]
     Then we expect 4 hits

     When I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_n}")]
     Then we expect 4 hits

     When I delete my selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_p}")]
     Then we expect 1 hits

     When I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_e}")]
     Then we expect 2 hits

Scenario Tag query two
    ${base_option_selector}=    Set Variable    select2-results-dept-0 select2-result select2-result-selectable select2-option
    ${base_option_selector_o}=    Set Variable    ${base_option_selector}-o
    ${base_option_selector_n}=    Set Variable    ${base_option_selector}-n
    ${base_option_selector_p}=    Set Variable    ${base_option_selector}-p
    ${base_option_selector_e}=    Set Variable    ${base_option_selector}-e
    # tests the "Matches all of" option
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I expect an empty result after open the operator Matches all of in the criteria Tag
      and I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_o}")]
     Then we expect 4 hits

     When I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_n}")]
     Then we expect 3 hits

     When I delete my selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_p}")]
     Then we expect 1 hits

     When I open the Selection Widget
      and Click    //li[contains(@class,"${base_option_selector_e}")]
     Then we expect 1 hits


Scenario Event end date query
    Given a logged-in manager
      and a bunch of events
      and the querystring pattern
    # Before date
     When I activate the default operator in the criteria Event end date
      and Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date"]
 ...    (element) => {
 ...        # fire the event for the browser build-in date input field
 ...        element.value="2018-07-01";
 ...        element.dispatchEvent(new Event("change", { bubbles: true }));
 ...    }
 ...    all_elements=False

     Then we do not expect any hits

    # When Execute Javascript  $('.querystring-criteria-value input[type="date"]').val('2018-07-06')

    # !!! BUG in plone.app.robotframework ?
    # File "~/.buildout/shared-eggs/plone.app.event-3.2.1-py3.6.egg/plone/app/event/recurrence.py", line 77, in occurrences
    #     duration = event_end - event_start
    # TypeError: can't subtract offset-naive and offset-aware datetimes

    #      When Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date"]
    #  ...    (element) => {
    #  ...        # fire the event for the browser build-in date input field
    #  ...        element.value="2018-08-06";
    #  ...        element.dispatchEvent(new Event("change", { bubbles: true }));
    #  ...    }
    #  ...    all_elements=False
    #      Then we expect 2 hits

    #     # Between dates
    #      When I activate the operator Between dates in the criteria Event end date
    #       and Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date" and contains(@class,"querystring-criteria-value-DateRangeWidget-start")]
    #  ...    (element) => {
    #  ...        # fire the event for the browser build-in date input field
    #  ...        element.value="2018-08-01";
    #  ...        element.dispatchEvent(new Event("change", { bubbles: true }));
    #  ...    }
    #  ...    all_elements=False
    #       and Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date" and contains(@class,"querystring-criteria-value-DateRangeWidget-end")]
    #  ...    (element) => {
    #  ...        # fire the event for the browser build-in date input field
    #  ...        element.value="2018-08-07";
    #  ...        element.dispatchEvent(new Event("change", { bubbles: true }));
    #  ...    }
    #  ...    all_elements=False
    #      Then we expect 3 hits

    #     # Between dates
    #      When I activate the operator Between dates in the criteria Event end date
    #       and Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date" and contains(@class,"querystring-criteria-value-DateRangeWidget-start")]
    #  ...    (element) => {
    #  ...        # fire the event for the browser build-in date input field
    #  ...        element.value="2018-08-06";
    #  ...        element.dispatchEvent(new Event("change", { bubbles: true }));
    #  ...    }
    #  ...    all_elements=False
    #       and Evaluate Javascript    //div[contains(@class,"querystring-criteria-value")]//input[@type="date" and contains(@class,"querystring-criteria-value-DateRangeWidget-end")]
    #  ...    (element) => {
    #  ...        # fire the event for the browser build-in date input field
    #  ...        element.value="2018-08-06";
    #  ...        element.dispatchEvent(new Event("change", { bubbles: true }));
    #  ...    }
    #  ...    all_elements=False
    #      Then we expect 2 hits



Scenario Short name (id) query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I open the criteria Short name (id)
      and I search for a
     Then I see A in Preview

Scenario Review state query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I open the criteria Review State
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-private")]
     Then we expect 7 hits

Scenario Type query
    Given a logged-in site administrator
      and a bunch of events
      and the querystring pattern
     When I open the criteria Type
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-event")]
     Then we expect 4 hits

     When I delete one selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-file")]
     Then we do not expect any hits

     When I delete one selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-folder")]
     Then we expect 5 hits

     When I delete one selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-link")]
     Then we expect 1 hits

     When I delete one selection
      and I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-document")]
     Then we expect 2 hits

     When I open the Selection Widget
      and Click    //li[contains(@class,"select2-option-link")]
     Then we expect 3 hits

Scenario Creator query
    Given a logged-in site administrator
      and a bunch of folders
      and the querystring pattern
     When I activate the default operator in the criteria Creator
     Then we expect 6 hits


*** Keywords ***

# GIVEN

a bunch of folders
    #We create enough items to give meaningful test results
    ${F1}=    Create content
    ...    type=Folder
    ...    title=A
    ...    description=a
    ...    subject=onep
    ${F2}=    Create content
    ...    type=Folder
    ...    title=B
    ...    description=b
    ...    subject=one
    ...    container=${F1}
    ${F3}=    Create content
    ...    type=Folder
    ...    title=C
    ...    description=and
    ...    subject=on
    ...    container=${F2}
    Create content
    ...    type=Document
    ...    title=D
    ...    subject=o
    ...    container=${F3}
    Create content
    ...    type=Document
    ...    title=E
    ...    container=${F3}
    Create content
    ...    type=Link
    ...    title=Link
    ...    remoteUrl=/front-page
    ...    container=${F3}
    [Return]  ${F1}


a bunch of events
    ${F1}=  a bunch of folders
    Create content
    ...    type=Event
    ...    title=Event1
    ...    start=2018-08-01T15:00
    ...    end=2018-08-01T17:00
    ...    container=${F1}
    Create content
    ...    type=Event
    ...    title=Event2
    ...    start=2018-08-05T16:00
    ...    end=2018-08-07T11:00
    ...    container=${F1}
    Create content
    ...    type=Event
    ...    title=Event3
    ...    start=2018-08-05T16:30
    ...    open_end-empty-marker=1
    ...    container=${F1}
    Create content
    ...    type=Event
    ...    title=Event4
    ...    start=2018-08-06
    ...    end=2018-08-06
    ...    whole_day-empty-marker=1
    ...    container=${F1}

the querystring pattern
    # We go the /a to give more useful query results
    Go to    ${PLONE_URL}/a/++add++Collection
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Type Text    //input[@id="form-widgets-IDublinCore-title"]    A Collection

# WHEN

I activate the operator ${OPERATOR} in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}
    mark results
    open the select box titled operator
    select index type ${OPERATOR}


I search in ${NAME} subfolder in the related item widget
    mark results
    Click    //div[@id="formfield-form-widgets-ICollection-query"]//div[@class="pat-relateditems-container"]//button[contains(@class,"mode") and contains(@class,"search")]
    Type Text     //div[contains(@class,"querystring-criteria-value-ReferenceWidget")]//li[@class="select2-search-field"]//input[contains(@class,"select2-input")]    ${NAME}
    Click    //ul[@class="select2-results"]//a[contains(@class,"pat-relateditems-result-select") and contains(@class,"selectable")]


I open the select box titled operator
    open the select box titled operator


I select index Simple
    select index type Simple


I open the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}


I search for ${KEYWORD}
    ${element}    Get Element    //input[contains(@class,"querystring-criteria-value-StringWidget")]
    Click    ${element}
    Type Text    ${element}    ${KEYWORD}
    Click    //div[@id="content-core"]


I activate the default operator in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}


I open the Selection Widget
    Click    //div[contains(@class,"select2-container-multi") and contains(@class,"querystring-criteria-value-MultipleSelectionWidget")]


I delete my selection
    #deletes two elements
    Click    (//div[contains(@class,"querystring-criteria-value-MultipleSelectionWidget")]//a[contains(@class,"select2-search-choice-close")])[1]
    Sleep  0.1
    Click    //div[contains(@class,"querystring-criteria-value-MultipleSelectionWidget")]//a[contains(@class,"select2-search-choice-close")]


I delete one selection
    # :visible -  should this be checked?
    Click    //div[contains(@class,"querystring-criteria-value-MultipleSelectionWidget")]//a[contains(@class,"select2-search-choice-close")]


I expect an empty result after open the operator ${OPERATOR} in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}
    Wait For Condition    Element Count    //dl[@class="searchResults"]    should be    0
    open the select box titled operator
    select index type ${OPERATOR}


# THEN

we expect ${NUM} hits
    #This assumes we have the 2 "Test document" and "Test folder" items from the
    #robot setup, as well as the 4 additional items from the "a bunch of folders" macro
    #works only for ${NUM} > 0
    # we need as `Sleep`, the select2 js is very slow
    Sleep    0.5s
    Wait until result is no longer marked
    ${hits}=    Evaluate Javascript    //dl[@class="searchResults"]
 ...    (element) => {
 ...        return document.querySelectorAll(".searchResults > dd").length
 ...    }
 ...    all_elements=False
    Should Be Equal As Integers    ${hits}    ${NUM}
    mark results

we do not expect any hits
    [Documentation]  The search results may be the previous results that are still visible for a short time, so sleep a bit.  Alternatively look at http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    Sleep    0.2
    Get Text    //div[@id="search-results"]    contains    No results were found.

I expect to be in Advanced mode
    open the select box titled operator
    ${element}=    Get Element    //div[contains(@class,"select2-drop-active") and contains(@style,"display: block;")]
    Get Text    ${element}    contains    Navigation Path
    Get Text    ${element}    contains    Absolute Path
    Get Text    ${element}    contains    Relative Path
    Get Text    ${element}    contains    Simple Mode
    Click    //div[@id="select2-drop-mask"]
    Get Element States    //div[@id="select2-drop-mask"]    contains    hidden

I expect to be in Simple mode
    open the select box titled operator
    ${element}=    Get Element    //div[contains(@class,"select2-drop-active") and contains(@style,"display: block;")]
    Get Text    ${element}    contains    Custom
    Get Text    ${element}    contains    Parent (../)
    Get Text    ${element}    contains    Current (./)
    Get Text    ${element}    contains    Advanced Mode
    Click    //div[@id="select2-drop-mask"]
    Get Element States    //div[@id="select2-drop-mask"]    contains    hidden

I see ${TEXT} in Preview
    Sleep    0.2
    Get Text    //div[@id="search-results"]    contains    ${TEXT}
# Helper

open the select box titled ${NAME}
    Click    //body
    Click    (//div[@class="querystring-criteria-${NAME}"])[1]//div[contains(@class,"select2-container")]

select index type ${INDEX}
    Type Text    //div[contains(@class,"select2-drop-active") and contains(@style, "display: block;")]//input    ${INDEX}
    Click    //*[contains(@class,"select2-match")]

mark results
    Evaluate Javascript    //dl[@class="searchResults"]
 ...    (element) => {
 ...        element.setAttribute("marker", "marked")
 ...    }
 ...    all_elements=False

wait until result is no longer marked
    Evaluate Javascript    //dl[@class="searchResults"]
 ...    (element) => {
 ...        return element && element.getAttribute("marker") != "marked"
 ...    }
 ...    all_elements=False
