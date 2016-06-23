*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Open SauceLabs test browser  Refresh JS/CSS resources
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases **************************************************************

Scenario: Location query
    Given a logged-in site administrator
    and a bunch of folders
    and the querystring pattern
    When I open the Current operator in the Location criteria
    Then we expect 1 hits
    When I open the Parent operator in the Location criteria
    Then we expect 3 hits
    When I open the Custom operator in the Location criteria
    and I search in A subfolder in the related items widget
    Then we expect 3 hits
    When I open the Advanced operator in the Location criteria
    Then I expect to be in Advanced mode
    When I open the Simple operator in the Location criteria
    Then I expect to be in Simple mode

*** Keywords ****************************************************************

the querystring pattern
    #We go the /a to give more useful query results
    Go to  ${PLONE_URL}/a/++add++Collection
    Wait until page contains element  css=.pat-querystring
    Given querystring pattern loaded

querystring pattern loaded
    Wait For Condition  return $('.querystring-criteria-remove').size() > 0

a bunch of folders
    #We create enough items to give meaningful test results
    ${F1}=  Create content  type=Folder  title=A
    ${F2}=  Create content  type=Folder  title=B  container=${F1}
    ${F3}=  Create content  type=Folder  title=C  container=${F2}
    Create content  type=Document  title=D  container=${F3}

I open the ${OPERATOR} operator in the ${CRITERIA} criteria
    open the select box titled index
    select index type ${CRITERIA}
    open the select box titled operator
    select index type ${OPERATOR}

I search in ${NAME} subfolder in the related items widget
    Click Element  jquery=.pattern-relateditems-tree-select
    Wait Until Element Is Visible  jquery=.pat-tree li.jqtree_common:contains("${NAME}") .pattern-relateditems-result-browse
    Click Element  jquery=.pat-tree li.jqtree_common:contains("${NAME}") .pattern-relateditems-result-browse
    Wait Until Element Is Visible  css=.pattern-relateditems-result-select
    Click Element  css=.pattern-relateditems-result-select

I expect to be in Advanced mode
    open the select box titled operator
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Navigation Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Absolute Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Relative Path
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Simple Mode
    Click Element  css=body
    Sleep  1

I expect to be in Simple mode
    open the select box titled operator
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Custom
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Parent (../)
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Current (./)
    Element Should Contain  jquery=.select2-drop-active[style*="display: block;"]   Advanced Mode
    Click Element  css=body

open the select box titled ${NAME}
    Click Element  css=.querystring-criteria-${NAME} .select2-container a

select index type ${INDEX}
    Input Text  jquery=.select2-drop-active[style*="display: block;"] input   text=${INDEX}
    Press Key  jquery=:focus  \\13

we expect ${NUM} hits
    #This assumes we have the 2 "Test document" and "Test folder" items from the
    #robot setup, as well as the 4 additional items from the "a bunch of folders" macro
    Sleep   1
    ${hits}=    Execute Javascript  return $('.searchResults > dd').size().toString();
    Should Be Equal     ${hits}     ${NUM}
