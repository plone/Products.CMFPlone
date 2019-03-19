*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

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
    and Wait Until Element Is Visible  css=div.querystring-preview
    and Click Element  css=div.querystring-preview
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
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-o
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-o
    Then we expect 4 hits
    When I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-n
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-n
    Then we expect 4 hits
    When I delete my selection
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-p
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-p
    Then we expect 1 hits
    When I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-e
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-e
    Then we expect 2 hits

Scenario Tag query two
    # tests the "Matches all of" option
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I expect an empty result after open the operator Matches all of in the criteria Tag
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-o
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-o
    Then we expect 4 hits
    When and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-n
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-n
    Then we expect 3 hits
    When I delete my selection
    and and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-p
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-p
    Then we expect 1 hits
    When and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-e
    and Click Element  css=li.select2-results-dept-0.select2-result.select2-result-selectable.select2-option-e
    Then we expect 1 hits


Scenario Event end date query
    Given a logged-in manager
    and a bunch of events
    and the querystring pattern
    # Before date
    When I activate the default operator in the criteria Event end date
    and Execute Javascript  $('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]').pickadate('picker').set('select', new Date(2018, 7, 1))
    Then we do not expect any hits

    # When Execute Javascript  $('.querystring-criteria-value .pattern-pickadate-date-wrapper > input[type="text"]').pickadate('picker').set('select', new Date(2018, 7, 6))

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
    and Wait Until Element Is Visible  css=li.select2-option-private
    and Click Element  css=li.select2-option-private
    Then we expect 7 hits

Scenario Type query
    Given a logged-in site administrator
    and a bunch of events
    and the querystring pattern
    When I open the criteria Type
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-event
    and Click Element  css=li.select2-option-event
    Then we expect 4 hits
    When I delete one selection
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-file
    and Click Element  css=li.select2-option-file
    Then we do not expect any hits
    When I delete one selection
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-folder
    and Click Element  css=li.select2-option-folder
    Then we expect 5 hits
    When I delete one selection
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-link
    and Click Element  css=li.select2-option-link
    Then we expect 1 hits
    When I delete one selection
    and I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-document
    and Click Element  css=li.select2-option-document
    Then we expect 2 hits
    When I open the Selection Widget
    and Wait Until Element Is Visible  css=li.select2-option-link
    and Click Element  css=li.select2-option-link
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
    Wait until page contains element  css=.pat-querystring
    Given querystring pattern loaded
    # for some unknown reason unload protection pops up, but only in robot tests
    Execute Javascript  $(window).unbind('beforeunload')

querystring pattern loaded
    Wait For Condition  return window.jQuery('.querystring-criteria-remove').size() > 0

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
    Create content  type=Event  title=Event1  start=2018-08-01 15:00  end=2018-08-01 17:00  container=${F1}
    Create content  type=Event  title=Event2  start=2018-08-05 16:00  end=2018-08-07 11:00  container=${F1}
    Create content  type=Event  title=Event3  start=2018-08-05 16:30  open_end-empty-marker=1  container=${F1}
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
    Wait Until Element Is Visible  css=input.querystring-criteria-value-StringWidget
    Click Element  css=input.querystring-criteria-value-StringWidget
    Input Text  css=input.querystring-criteria-value-StringWidget  ${KEYWORD}
    Click Element  css=div#content-core

I open the Selection Widget
    wait until element is visible  css=div.select2-container-multi.querystring-criteria-value-MultipleSelectionWidget
    click element  css=div.select2-container-multi.querystring-criteria-value-MultipleSelectionWidget

I delete one selection
    #deletes one element
    Click Element  css=a.select2-search-choice-close

I delete my selection
    #deletes two elements
    Click Element  css=a.select2-search-choice-close
    Click Element  css=a.select2-search-choice-close

I search in ${NAME} subfolder in the related items widget
    mark results
    Click Element  css=ul.select2-choices
    Wait Until Page Contains  ${NAME}
    Click Element  //a[contains(concat(' ', normalize-space(@class), ' '), ' pattern-relateditems-result-select ')]//span[contains(text(),'${NAME}')]

I expect to be in Advanced mode
    open the select box titled operator
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Navigation Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Absolute Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Relative Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Simple Mode
    Click Element  css=div#select2-drop-mask
    Wait Until Element Is Not Visible  css=div#select2-drop-mask

I expect to be in Simple mode
    open the select box titled operator
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Custom
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Parent (../)
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Current (./)
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Advanced Mode
    Click Element  css=div#select2-drop-mask
    Wait Until Element Is Not Visible  css=div#select2-drop-mask

open the select box titled ${NAME}
    Click Element  css=body
    Click Element  css=.querystring-criteria-${NAME} .select2-container a

select index type ${INDEX}
    Input Text  jquery=.select2-drop-active[style*="display: block;"] input   text=${INDEX}
    Press Key  jquery=:focus  \\13

we expect ${NUM} hits
    #This assumes we have the 2 "Test document" and "Test folder" items from the
    #robot setup, as well as the 4 additional items from the "a bunch of folders" macro
    #works only for ${NUM} > 0
    Wait until result is no longer marked
    ${hits}=  Execute Javascript  return $('.searchResults > dd').length
    Should Be Equal As Integers  ${hits}  ${NUM}
    mark results

we do not expect any hits
    Wait Until Element Is Visible  css=div#search-results
    Wait Until Element Contains  css=div#search-results  No results were found.

a logged-in manager
    Enable autologin as  Manager  Site Administrator  Contributor  Reviewer

mark results
    Wait for condition  return $("dl.searchResults").length > 0
    Execute Javascript  $("dl.searchResults").attr("marker", "marked")

wait until result is no longer marked
    Wait for condition  return $("dl.searchResults").length > 0 && $("dl.searchResults").attr("marker") != "marked"