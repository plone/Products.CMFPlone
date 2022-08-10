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
  # Sleep to avoid random failures where the text is not actually set.
  # This warning from the robotframework docs might be the cause:
  # "Starting from Robot Framework 2.5 errors caused by invalid syntax, timeouts,
  # or fatal exceptions are not caught by this keyword."
  # See https://robotframework.org/robotframework/2.6.1/libraries/BuiltIn.html#Wait%20Until%20Keyword%20Succeeds
  Sleep  1
  Wait until keyword succeeds  5s  1s  Set and Check TinyMCE Content  ${input}

Set and Check TinyMCE Content
  [Arguments]  ${input}
  # Simply check if tinyMCE.getContent() isn't empty when we set an input
  Execute Javascript   tinyMCE.activeEditor.setContent('${input}');
  Sleep  0.5
  ${check}=  Execute Javascript  return tinyMCE.activeEditor.getContent();
  Should not be empty  ${check}


# --- WHEN -------------------------------------------------------------------

I add '${tag}' to the nasty tags list and remove it from the valid tags list
  Input Text  name=form.widgets.nasty_tags  ${tag}
  Remove line from textarea  form.widgets.valid_tags  ${tag}
  I save the form

I remove '${tag}' from the valid tags list
  Remove line from textarea  form.widgets.valid_tags  ${tag}
  I save the form

I add '${tag}' to the valid tags list
  Input Text  name=form.widgets.valid_tags  ${tag}
  I save the form
  Page Should Contain  ${tag}

I add '${tag}' to the custom attributes list
  Input Text  name=form.widgets.custom_attributes  ${tag}
  I save the form
  Page Should Contain  ${tag}

I save the form
  Wait For Then Click Element  form.buttons.save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the 'h1' tag is filtered out when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h1>h1 heading</h1><p>Spanish Inquisition</p>
  I save the form
  # We check that some standard text is there, before checking the interesting part.
  # If the standard text is invisible, then something completely different is wrong.
  # I see tests randomly fail where the safe html transform is not even called.
  # In fact, no text is saved.  Maybe some timing problem.
  # I suspect the Input RichText keyword, which is why I added Sleep in there.
  Page should contain  Spanish Inquisition
  Page should not contain  heading

the 'h1' tag is stripped when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <h1>h1 heading</h1><p>Spanish Inquisition</p>
  I save the form
  Page should contain  Spanish Inquisition
  Page should contain  heading
  Page Should Contain Element  //div[@id='content-core']//h1  limit=0  message=h1 should have been stripped out

the '${tag}' tag is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <${tag}>lorem ipsum</${tag}><p>Spanish Inquisition</p>
  I save the form
  Page should contain  Spanish Inquisition
  Page Should Contain Element  //div[@id='content-core']//${tag}  limit=1  message=the ${tag} tag should have been preserved

the '${attribute}' attribute is preserved when a document is saved
  ${doc1_uid}=  Create content  id=doc1  title=Document 1  type=Document
  Go To  ${PLONE_URL}/doc1/edit
  patterns are loaded
  Input RichText  <span ${attribute}="foo">lorem ipsum</span><p>Spanish Inquisition</p>
  I save the form
  Page should contain  Spanish Inquisition
  Page Should Contain Element  //span[@${attribute}]  limit=1  message=the ${attribute} tag should have been preserved

success message should contain information regarding caching
  Element Should Contain  css=.alert-warning  HTML generation is heavily cached across Plone. You may have to edit existing content or restart your server to see the changes.
