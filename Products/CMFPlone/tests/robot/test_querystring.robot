*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown

*** Test Cases **************************************************************

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
    and I search in B subfolder in the related items widget
    Then we expect 5 hits

Scenario: Location query Advanced
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I activate the operator Advanced in the criteria Location
    Then I expect to be in Advanced mode

Scenario: Location query Simple
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I activate the operator Simple in the criteria Location
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
    ${preview_selector}  Set Variable  div.querystring-preview
    Set Focus To Element  css=${preview_selector}
    and Wait Until Element Is Visible  css=${preview_selector}
    and Click Element  css=${preview_selector}
    Then we expect 2 hits
    When I open the criteria Searchable text
    and I search for d
    Then we expect 1 hits

Scenario: Tag query one
    # tests the "Matches any of" option
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I activate the default operator in the criteria Tag
    and I open the Selection Widget
    ${base_option_selector}  Set Variable  li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option
    Set Focus To Element  css=${base_option_selector}-o
    and Wait Until Element Is Visible  css=${base_option_selector}-o
    and Click Element  css=${base_option_selector}-o
    Then we expect 4 hits
    When I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-n
    and Wait Until Element Is Visible  css=${base_option_selector}-n
    and Click Element  css=${base_option_selector}-n
    Then we expect 4 hits
    When I delete my selection
    and I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-p
    and Wait Until Element Is Visible  css=${base_option_selector}-p
    and Click Element  css=${base_option_selector}-p
    Then we expect 1 hits
    When I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-e
    and Wait Until Element Is Visible  css=${base_option_selector}-e
    and Click Element  css=${base_option_selector}-e
    Then we expect 2 hits

Scenario Tag query two
    # tests the "Matches all of" option
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I expect an empty result after open the operator Matches all of in the criteria Tag
    and I open the Selection Widget
    ${base_option_selector}  Set Variable  li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option
    Set Focus To Element  css=${base_option_selector}-o
    and Wait Until Element Is Visible  css=${base_option_selector}-o
    and Click Element  css=${base_option_selector}-o
    Then we expect 4 hits
    When and I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-n
    and Wait Until Element Is Visible  css=${base_option_selector}-n
    and Click Element  css=${base_option_selector}-n
    Then we expect 3 hits
    When I delete my selection
    and and I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-p
    and Wait Until Element Is Visible  css=${base_option_selector}-p
    and Click Element  css=${base_option_selector}-p
    Then we expect 1 hits
    When and I open the Selection Widget
    Set Focus To Element  css=${base_option_selector}-e
    and Wait Until Element Is Visible  css=${base_option_selector}-e
    and Click Element  css=${base_option_selector}-e
    Then we expect 1 hits


Scenario Event end date query
    Given a logged-in manager
    and a bunch of events
    and the querystring pattern
    # Before date
    When I activate the default operator in the criteria Event end date
    and Execute Javascript  $('.querystring-criteria-value input[type="date"]').val('2018-07-01')
    Then we do not expect any hits

    # When Execute Javascript  $('.querystring-criteria-value input[type="date"]').val('2018-07-06')

    # !!! BUG in plone.app.robotframework?
    # File "~/.buildout/shared-eggs/plone.app.event-3.2.1-py3.6.egg/plone/app/event/recurrence.py", line 77, in occurrences
    #     duration = event_end - event_start
    # TypeError: can't subtract offset-naive and offset-aware datetimes

    # for some reason the timezone is not applied correctly here. this is
    # probably a problem with plone.app.robotframework.content creation mechanism.
    # actually we got 3 hits, but right would be:
    # Then we expect 2 hits
    # Between dates
    # When I activate the operator Between dates in the criteria Event end date
    # and Execute Javascript  $($('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]')[0]).pickadate('picker').set('select', new Date(2018, 7, 1))
    # and Execute Javascript  $($('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]')[1]).pickadate('picker').set('select', new Date(2018, 7, 7))
    # Then we expect 3 hits
    # When Execute Javascript  $($('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]')[0]).pickadate('picker').set('select', new Date(2018, 7, 6))
    # and Execute Javascript  $($('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]')[1]).pickadate('picker').set('select', new Date(2018, 7, 8))
    # Then we expect 2 hits

Scenario Short name (id) query
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I open the criteria Short name (id)
    And I search for a
    Then Page Should Contain  A

Scenario Review state query
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I open the criteria Review State
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-private
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 7 hits

Scenario Type query
    Given a logged-in site administrator
    and a bunch of events
    and the querystring pattern
    When I open the criteria Type
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-event
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 4 hits
    When I delete one selection
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-file
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we do not expect any hits
    When I delete one selection
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-folder
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 5 hits
    When I delete one selection
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-link
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 1 hits
    When I delete one selection
    and I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-document
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 2 hits
    When I open the Selection Widget
    ${query_selector}  Set Variable  li.select2-option-link
    Set Focus To Element  css=${query_selector}
    and Wait Until Element Is Visible  css=${query_selector}
    and Click Element  css=${query_selector}
    Then we expect 3 hits

Scenario Creator query
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I activate the default operator in the criteria Creator
    Then we expect 6 hits


*** Keywords ****************************************************************

save
    Click Link  css=input#form-buttons-save

the querystring pattern
    #We go the /a to give more useful query results
    Go to  ${PLONE_URL}/a/++add++Collection
    ${pattern_selector}  Set Variable  .pat-querystring
    Set Focus To Element  css=${pattern_selector}
    Wait until page contains element  css=${pattern_selector}
    Given querystring pattern loaded
    # for some unknown reason unload protection pops up, but only in robot tests
    Execute Javascript  $(window).unbind('beforeunload')

querystring pattern loaded
    Wait For Condition  return !!document.querySelector('.querystring-criteria-remove')

a bunch of folders
    #We create enough items to give meaningful test results
    ${F1}=  Create content  type=Folder  title=A  description=a  subject=onep
    ${F2}=  Create content  type=Folder  title=B  description=b  subject=one  container=${F1}
    ${F3}=  Create content  type=Folder  title=C  description=and  subject=on  container=${F2}
    Create content  type=Document  title=D  subject=o  container=${F3}
    Create content  type=Document  title=E  container=${F3}
    Create content  type=Link  title=Link  remoteUrl=/front-page  container=${F3}
    [Return]  ${F1}

a bunch of events
    ${F1}=  a bunch of folders
    Create content  type=Event  title=Event1  start=2018-08-01T15:00  end=2018-08-01T17:00  container=${F1}
    Create content  type=Event  title=Event2  start=2018-08-05T16:00  end=2018-08-07T11:00  container=${F1}
    Create content  type=Event  title=Event3  start=2018-08-05T16:30  open_end-empty-marker=1  container=${F1}
    Create content  type=Event  title=Event4  start=2018-08-06  end=2018-08-06  whole_day-empty-marker=1  container=${F1}

I activate the default operator in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}

I activate the operator ${OPERATOR} in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}
    mark results
    open the select box titled operator
    select index type ${OPERATOR}

I expect an empty result after open the operator ${OPERATOR} in the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}
    sleep  0.75
    Wait for condition  return $("dl.searchResults").length == 0
    open the select box titled operator
    select index type ${OPERATOR}

I open the criteria ${CRITERIA}
    open the select box titled index
    select index type ${CRITERIA}

I search for ${KEYWORD}
    ${keyword_selector}  Set Variable  input.querystring-criteria-value-StringWidget
    Set Focus To Element  css=${keyword_selector}
    Wait Until Element Is Visible  css=${keyword_selector}
    Click Element  css=${keyword_selector}
    Input Text  css=${keyword_selector}  ${KEYWORD}
    Click Element  css=div#content-core

I open the Selection Widget
    ${widget_selector}  Set Variable  div.select2-container-multi.querystring-criteria-value-MultipleSelectionWidget
    Set Focus To Element  css=${widget_selector}
    wait until element is visible  css=${widget_selector}
    click element  css=${widget_selector}

I delete one selection
    #deletes one element
    ${selection_selector}  Set Variable  a.select2-search-choice-close
    Set Focus To Element  css=${selection_selector}
    Click Element  css=${selection_selector}

I delete my selection
    #deletes two elements
    ${selection_selector}  Set Variable  a.select2-search-choice-close
    Set Focus To Element  css=${selection_selector}
    Click Element  css=${selection_selector}
    Sleep  0.1
    Set Focus To Element  css=${selection_selector}
    Click Element  css=${selection_selector}

I search in ${NAME} subfolder in the related items widget
    mark results
    ${selector}  Set Variable  ul.select2-choices
    Set Focus To Element  css=${selector}
    Click Element  css=${selector}
    Wait Until Page Contains  ${NAME}
    Click Element  //a[contains(concat(' ', normalize-space(@class), ' '), ' pat-relateditems-result-select ')]//span[contains(text(),'${NAME}')]

I expect to be in Advanced mode
    open the select box titled operator
    ${selector}  Set Variable  .select2-drop-active[style*="display: block;"]
    Element Should Contain  jquery=${selector}   Navigation Path
    Element Should Contain  jquery=${selector}   Absolute Path
    Element Should Contain  jquery=${selector}   Relative Path
    Element Should Contain  jquery=${selector}   Simple Mode
    ${selector}  Set Variable  div#select2-drop-mask
    Set Focus To Element  css=${selector}
    Click Element  css=${selector}
    Wait Until Element Is Not Visible  css=${selector}

I expect to be in Simple mode
    open the select box titled operator
    ${selector}  Set Variable  .select2-drop-active[style*="display: block;"]
    Element Should Contain  jquery=${selector}   Custom
    Element Should Contain  jquery=${selector}   Parent (../)
    Element Should Contain  jquery=${selector}   Current (./)
    Element Should Contain  jquery=${selector}   Advanced Mode
    ${selector}  Set Variable  div#select2-drop-mask
    Set Focus To Element  css=${selector}
    Click Element  css=${selector}
    Wait Until Element Is Not Visible  css=${selector}

open the select box titled ${NAME}
    Click Element  css=body
    ${select_criteria_selector}  Set Variable  .querystring-criteria-${NAME} .select2-container
    Set Focus To Element  css=${select_criteria_selector}
    Wait Until Element Is Visible  css=${select_criteria_selector}
    Click Element  css=${select_criteria_selector}

select index type ${INDEX}
    ${input_selector}  Set Variable  .select2-drop-active[style*="display: block;"] input
    Set Focus To Element  css=${input_selector}
    Wait Until Element Is Visible  css=${input_selector}
    Input Text  css=${input_selector}   text=${INDEX}
    Press Keys  jquery=:focus  RETURN

we expect ${NUM} hits
    #This assumes we have the 2 "Test document" and "Test folder" items from the
    #robot setup, as well as the 4 additional items from the "a bunch of folders" macro
    #works only for ${NUM} > 0
    Sleep  0.5s
    Wait until result is no longer marked
    ${hits}=  Execute Javascript  return $('.searchResults > dd').length
    Should Be Equal As Integers  ${hits}  ${NUM}
    mark results

we do not expect any hits
    [Documentation]  The search results may be the previous results that are still visible for a short time, so sleep a bit.  Alternatively look at http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    Sleep  0.2
    Wait Until Element Is Visible  css=div#search-results
    Wait Until Element Contains  css=div#search-results  No results were found.

a logged-in manager
    Enable autologin as  Manager  Site Administrator  Contributor  Reviewer

mark results
    Wait for condition  return $("dl.searchResults").length > 0
    Execute Javascript  $("dl.searchResults").attr("marker", "marked")

wait until result is no longer marked
    Wait for condition  return $("dl.searchResults").length > 0 && $("dl.searchResults").attr("marker") != "marked"
