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

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Configure Filter Control Panel to filter out nasty tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'h1' to the nasty tags list
   Then the 'h1' tag is filtered out when a document is saved

Scenario: Configure Filter Control Panel to strip out tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'h1' to the stripped tags list
   Then the 'h1' tag is stripped when a document is saved

Scenario: Configure Filter Control Panel to allow custom tags
  Given a logged-in site administrator
    and the filter control panel
   When I add 'marquee' to the custom tags list
   Then the 'marquee' tag is preserved when a document is saved

Scenario: Configure Filter Control Panel to strip out attributes
  Given a logged-in site administrator
    and the filter control panel
   When I add 'data-stripme' to the stripped attributes list
   Then the 'data-stripme' attribute is stripped when a document is saved

Scenario: Configure Filter Control Panel to allow style attributes
  Given a logged-in site administrator
    and the filter control panel
   When I add 'display' to the allowed style attributes
   Then the 'display' style attribute is preserved when a document is saved

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

Input RichText
  [Arguments]  ${input}
  Wait until keyword succeeds  5s  1s  Execute Javascript  tinyMCE.activeEditor.setContent('${input}');


# --- WHEN -------------------------------------------------------------------

I add '${tag}' to the nasty tags list
  Input Text  name=form.widgets.nasty_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the stripped tags list
  Input Text  name=form.widgets.stripped_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the custom tags list
  Input Text  name=form.widgets.custom_tags  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the stripped attributes list
  Input Text  name=form.widgets.stripped_attributes  ${tag}
  Click Button  Save
  Wait until page contains  Changes saved

I add '${tag}' to the allowed style attributes
  Input text  name=form.widgets.style_whitelist  ${tag}
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

the 'marquee' tag is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <marquee>lorem ipsum</marquee>
  Click Button  Save
  Wait until page contains  Changes saved
  XPath Should Match X Times  //div[@id='content-core']//marquee  1  message=the marquee tag should have been preserved

the 'data-stripme' attribute is stripped when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h4 data-stripme="foo">lorem ipsum</h4>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should contain  lorem ipsum

  XPath Should Match X Times  //*[@id='content-core']//h4  1  message=h4 tag should be present
  XPath Should Match X Times  //*[@id='content-core']//h4[@data-stripme='foo']  0  message=data-stripme attribute should have been filtered out

the 'foobar' class is filtered out when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h4 class="foobar">lorem ipsum</h4>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should contain  lorem ipsum

  XPath Should Match X Times  //*[@id='content-core']//h4  1  message=h4 tag should be present
  XPath Should Match X Times  //*[@id='content-core']//h4[@class='foobar']  0  message=class foobar should have been filtered out

the 'display' style attribute is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h4 style="display: block">lorem ipsum</h4>
  Click Button  Save
  Wait until page contains  Changes saved
  Page should contain  lorem ipsum

  XPath Should Match X Times  //*[@id='content-core']//h4  1  message=h4 tag should be present
  XPath Should Match X Times  //*[@id='content-core']//h4[@style]  1  message=style attribute with display:block should be present

success message should contain information regarding caching
  Element Should Contain  css=.portalMessage.warning  HTML generation is heavily cached across Plone. You may have to edit existing content or restart your server to see the changes.
