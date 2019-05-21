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
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library  Collections

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Configure Filter Control Panel to filter out nasty tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'h1' to the nasty tags list and remove it from the valid tags list
   Then the 'h1' tag is filtered out when a document is saved

Scenario: Configure Filter Control Panel to strip out tags
  Given a logged-in site administrator
    and the filter control panel
   When I remove 'h1' from the valid tags list
   Then the 'h1' tag is stripped when a document is saved

Scenario: Configure Filter Control Panel to allow custom tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'foobar' to the valid tags list
   Then the 'foobar' tag is preserved when a document is saved

Scenario: Configure Filter Control Panel to allow custom attributes
  Given a logged-in site administrator
    and the filter control panel
   When I add 'foo-foo' to the custom attributes list
   Then the 'foo-foo' attribute is preserved when a document is saved

Scenario: Filter Control Panel displays information regarding caching when saved
  Given a logged-in site administrator
    and the filter control panel
   When I save the form
   Then success message should contain information regarding caching


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the filter control panel
  Go to  ${PLONE_URL}/@@filter-controlpanel
  Wait until page contains  HTML Filtering Settings

Input RichText
  [Arguments]  ${input}
  Wait until keyword succeeds  5s  1s  Execute Javascript  tinyMCE.activeEditor.setContent('${input}');


# --- WHEN -------------------------------------------------------------------

I add '${tag}' to the nasty tags list and remove it from the valid tags list
  Input Text  name=form.widgets.nasty_tags  ${tag}
  Remove line from textarea  form.widgets.valid_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I remove '${tag}' from the valid tags list
  Remove line from textarea  form.widgets.valid_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the valid tags list
  Input Text  name=form.widgets.valid_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the custom attributes list
  Input Text  name=form.widgets.custom_attributes  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I save the form
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the 'h1' tag is filtered out when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h1>h1 heading</h1><p>lorem ipsum</p>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should not contain  heading

the 'h1' tag is stripped when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h1>h1 heading</h1><p>lorem ipsum</p>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should contain  heading
  XPath Should Match X Times  //div[@id='content-core']//h1  0  message=h1 should have been stripped out

the '${tag}' tag is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <${tag}>lorem ipsum</${tag}>
  Click Button  Save
  Wait until page contains  Changes saved
  XPath Should Match X Times  //div[@id='content-core']//${tag}  1  message=the ${tag} tag should have been preserved

the '${attribute}' attribute is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <span ${attribute}="foo">lorem ipsum</span>
  Click Button  Save
  Wait until page contains  Changes saved
  XPath Should Match X Times  //span[@${attribute}]  1  message=the ${attribute} tag should have been preserved

success message should contain information regarding caching
  Element Should Contain  css=.portalMessage.warning  HTML generation is heavily cached across Plone. You may have to edit existing content or restart your server to see the changes.
