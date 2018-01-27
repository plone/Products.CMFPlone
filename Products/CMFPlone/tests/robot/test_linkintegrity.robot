# ============================================================================
# Tests for the Plone Link Integrity Support
# ============================================================================
#
# $ bin/robot-server --reload-path src/Products.CMFPlone/Products/CMFPlone/ Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
#
# $ bin/robot src/Products.CMFPlone/Products/CMFPlone/tests/robot/test_linkintegrity.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

#Suite setup  Set Selenium speed  0.5s
Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: When page is linked show warning
  Given a logged-in site administrator
    and a page to link to
    and a page to edit
    and a link in rich text
    should show warning when deleting page


Scenario: After you fix linked page no longer show warning
  Given a logged-in site administrator
  a page to link to
    and a page to edit
    and a link in rich text
  should show warning when deleting page
    remove link to page
  should not show warning when deleting page


Scenario: Show warning when deleting linked item from folder_contents
  Given a logged-in site administrator
  a page to link to
    and a page to edit
    and a link in rich text
  should show warning when deleting page from folder_contents
    remove link to page
  should not show warning when deleting page from folder_contents


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator


a page to link to
  Create content  type=Document  id=foo  title=Foo

a page to edit
  Create content  type=Document  id=bar  title=Bar


a link in rich text
  Go To  ${PLONE_URL}/bar/edit
  Wait until element is visible  css=.mce-edit-area iframe
  Select Frame  css=.mce-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame
  Click Button  css=div[aria-label="Insert/edit link"] button

  Given patterns are loaded
  Wait until element is visible  css=.pat-relateditems .select2-input.select2-default
  Click Element  css=.pat-relateditems .select2-input.select2-default
  Wait until element is visible  xpath=(//span[contains(., 'One level up')])
  Click Element  xpath=(//span[contains(., 'One level up')])
  Wait until element is visible  xpath=(//span[contains(., 'Foo')])
  Click Element  xpath=(//span[contains(., 'Foo')])
  Wait until page contains  Foo

  Click Button  css=.plone-modal-footer .plone-btn-primary
  Click Button  css=#form-buttons-save


should show warning when deleting page
  Go To  ${PLONE_URL}/foo
  Click Link  css=#plone-contentmenu-actions a
  Click Link  css=#plone-contentmenu-actions-delete
  Wait until page contains element  css=.breach-container .breach-item


should show warning when deleting page from folder_contents
  Go To  ${PLONE_URL}/folder_contents
  Wait until keyword succeeds  30  1  Page should contain element  css=tr[data-id="foo"] input
  Click Element  css=tr[data-id="foo"] input
  Checkbox Should Be Selected  css=tr[data-id="foo"] input
  Wait until keyword succeeds  30  1  Page should not contain element  css=#btn-delete.disabled
  Click Element  css=#btngroup-mainbuttons #btn-delete
  Wait until page contains element  css=.popover-content .btn-danger
  Page should contain element  css=.breach-container .breach-item
  Click Element  css=#popover-delete .closeBtn
  Checkbox Should Be Selected  css=tr[data-id="foo"] input


should not show warning when deleting page from folder_contents
  Go To  ${PLONE_URL}/folder_contents
  Wait until page contains element  css=tr[data-id="foo"] input
  Click Element  css=tr[data-id="foo"] input
  Checkbox Should Be Selected  css=tr[data-id="foo"] input
  Wait until keyword succeeds  30  1  Page should not contain element  css=#btn-delete.disabled
  Click Element  css=#btngroup-mainbuttons #btn-delete
  Wait until page contains element  css=.popover-content .btn-danger
  Page should not contain element  css=.breach-container .breach-item
  Click Element  css=#popover-delete .applyBtn
  Wait until page contains  Successfully delete items
  Wait until keyword succeeds  30  1  Page should not contain Element  css=tr[data-id="foo"] input


should not show warning when deleting page
  Go To  ${PLONE_URL}/foo
  Click Link  css=#plone-contentmenu-actions a
  Click Link  css=#plone-contentmenu-actions-delete
  Page should not contain element  css=.breach-container .breach-item


remove link to page
  Go To  ${PLONE_URL}/bar
  Click Link  css=#contentview-edit a
  Wait until element is visible  css=.mce-edit-area iframe
  Select Frame  css=.mce-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame
  Click Button  css=div[aria-label="Remove link(s)"] button
  Click Button  css=#form-buttons-save
