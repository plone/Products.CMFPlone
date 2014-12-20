# ============================================================================
# Tests for the Plone Filter Control Panel
# ============================================================================
#
# $ bin/robot-server --reload-path src/Products.CMFPlone/Products/CMFPlone/ Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
#
# $ bin/robot src/Products.CMFPlone/Products/CMFPlone/tests/robot/test_controlpanel_filter.robot
#
# ============================================================================

*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Configure Filter Control Panel to filter out nasty tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'h1' to the nasty tags list
   Then the 'h1' tag is filtered out when a document is saved

Scenario: Configure Filter Control Panel to filter out stripped tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'h1' to the stripped tags list
   Then the 'h1' tag is stripped when a document is saved


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the filter control panel
  Go to  ${PLONE_URL}/@@filter-controlpanel

Input RichText
  [Arguments]  ${input}
  Wait until keyword succeeds  5s  1s  Execute Javascript  tinyMCE.activeEditor.setContent('${input}');


# --- WHEN -------------------------------------------------------------------

I add '${tag}' to the nasty tags list
  Click Button  Add Nasty tags
  Input Text  name=form.nasty_tags.6.  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the stripped tags list
  Click Button  Add Stripped tags
  Input Text  name=form.stripped_tags.16.  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the 'h1' tag is filtered out when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  Input RichText  <h1>h1 heading</h1><p>lorem ipsum</p>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should not contain  heading

the 'h1' tag is stripped when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  Input RichText  <h1>h1 heading</h1><p>lorem ipsum</p>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should contain  heading
  XPath Should Match X Times  //div[@id='content-core']//h1  0  message=h1 should have been stripped out
