*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown

*** Variables ***

${LESS}     @color: blue; body { background: @color; }
${LESSFILE}     test.less
${CSSFILE}      output.less
${CSS}      background: blue;

*** Test Cases **************************************************************

Scenario: Thememapper basic functionality
    Given a logged-in site administrator
    and a new theme to edit
    When I open rules.xml
    Then I expect 2 tabs to be open
    and I expect a tab labeled "rules.xml" to be open

    When I close the tab labeled "rules.xml"
    Then I expect 1 tabs to be open

    When I create a new file called "${LESSFILE}"
    Then I expect 2 tabs to be open
    and I expect a tab labeled "${LESSFILE}" to be open

    When I type some code into the editor
    and I save the current document
    I expect the document ${LESSFILE} to contain ${LESS}

Scenario: Thememapper LESS builder
    Given a logged-in site administrator
    and a new theme to edit
    and I create a new file called "${LESSFILE}"
    and I type some code into the editor
    and I save the current document
    When I use the LESS builder on "${LESSFILE}"
    Then I expect the compiled CSS to contain "${CSS}"

*** Keywords ****************************************************************

a new theme to edit
    Go to  ${PLONE_URL}/theming-controlpanel
    Wait until page contains  Theme settings
    Click Element   jquery=a[href="#modal-copy-barceloneta"]
    Wait Until Element Is Visible   jquery=.plone-modal-body input[type="text"]
    Input Text  jquery=.plone-modal-body input[type="text"]   Test
    Click Element   jquery=.plone-modal-body input[type="submit"]
    Wait Until Element Is Visible   css=.nav-and-editor
    Page Should Contain     backend.xml

I open ${NAME}
    Click Element   jquery=.jqtree-element:contains("${NAME}")

I expect ${NUM} tabs to be open
    Sleep  1
    ${hits}=    Execute Javascript  return window.jQuery('.navbar-nav li').length.toString();
    Should Be Equal     ${hits}     ${NUM}

I expect a tab labeled "${LABEL}" to be open
    Wait Until Element Is Visible   jquery=.navbar-nav li:contains("${LABEL}")

I close the tab labeled "${LABEL}"
    Click Element   jquery=.navbar-nav li:contains("${LABEL}") .remove

I create a new file called "${NAME}"
    Click Element   css=#btngroup-main #btngroup-dropdown-file_menu #dropdown-menu-
    Click Element   css=#alink-addnew
    Input Text  jquery=.addnew input[type="text"]   ${NAME}
    Click Element   jquery=.addnew .btn-primary
    Sleep   1

I type some code into the editor
    Click Element   css=.ace_content
    ${ace_id}=     Execute Javascript   return window.jQuery('.ace_editor').attr('id');
    Execute Javascript      ace.edit(${ace_id}).setValue("${LESS}");

I expect the editors value to be "${MESSAGE}"
    ${ace_id}=      Execute Javascript  return window.jQuery('.ace_editor').attr('id');
    ${value}=   Execute Javascript      return ace.edit('${ace_id}').getValue();
    Should Be Equal     ${value}    ${MESSAGE}

I expect the editors value to contain "${MESSAGE}"
    ${ace_id}=      Execute Javascript  return window.jQuery('.ace_editor').attr('id');
    ${value}=   Execute Javascript      return ace.edit('${ace_id}').getValue();
    Should Contain  ${value}    ${MESSAGE}

I save the current document
    Click Element   css=#btn-save
    Sleep   1

I expect the document ${NAME} to contain ${MESSAGE}
    Go To   ${PLONE_URL}/++theme++test/@@theming-controlpanel-mapper
    Wait Until Element Is Visible    css=.ace_editor
    I open ${NAME}
    I expect the editors value to be "${MESSAGE}"

I use the LESS builder on "${file}"
    I open ${file}
    Click Element   css=#btngroup-mapper #btngroup-dropdown-file_menu #dropdown-menu-
    Click Element   css=#alink-buildless
    Input Text      css=#lessFileName   ${CSSFILE}
    Click element   css=#compileBtn
    Sleep   1

I expect the compiled CSS to contain "${TEXT}"
    I open ${CSSFILE}
    I expect the editors value to contain "${TEXT}"
