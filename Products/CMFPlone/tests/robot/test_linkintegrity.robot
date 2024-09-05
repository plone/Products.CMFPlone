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
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown

*** Variables ****************************************************************

${SELENIUM_RUN_ON_FAILURE}  Capture page screenshot and log source


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
  Wait until element is visible  css=.tox-edit-area iframe
  Select Frame  css=.tox-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame

  Click Button  css=button[aria-label="Insert/edit link"]
  Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
  Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
  Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
  Wait Until Element Is Not Visible    xpath=//div[contains(@class,"content-browser-position-wrapper")]
  Wait For Then Click Element  css=.modal-footer input[name="insert"]
  Select Frame  css=.tox-edit-area iframe
  Execute Javascript  window.getSelection().removeAllRanges()
  UnSelect Frame
  Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]
  Wait For Then Click Element  css=#form-buttons-save


should show warning when deleting page

  Go To  ${PLONE_URL}/foo
  Wait For Then Click Element  css=#plone-contentmenu-actions > a
  Wait For Then Click Element  css=#plone-contentmenu-actions-delete
  Wait until page contains element  css=.breach-container .breach-item


should show warning when deleting page from folder_contents
  Go To  ${PLONE_URL}/folder_contents
  Given folder contents pattern loaded
  Wait For Then Click Element  css=tr[data-id="foo"] input
  Checkbox Should Be Selected  css=tr[data-id="foo"] input
  Wait until keyword succeeds  30  1  Page should not contain element  css=#btn-delete.disabled

  Wait For Then Click Element  css=#btngroup-mainbuttons #btn-delete
  Wait until page contains element  css=.popover-content .btn-danger
  Page should contain element  css=.breach-container .breach-item
  Wait For Then Click Element  css=#popover-delete .closeBtn
  Checkbox Should Be Selected  css=tr[data-id="foo"] input


should not show warning when deleting page from folder_contents
  Go To  ${PLONE_URL}/folder_contents
  Given folder contents pattern loaded
  Wait For Then Click Element  css=tr[data-id="foo"] input
  Checkbox Should Be Selected  css=tr[data-id="foo"] input
  Wait until keyword succeeds  30  1  Page should not contain element  css=#btn-delete.disabled
  Wait For Then Click Element  css=#btngroup-mainbuttons #btn-delete
  Wait until page contains element  css=.popover-content .btn-danger
  Page should not contain element  css=.breach-container .breach-item
  Wait For Then Click Element  css=#popover-delete .applyBtn
  Wait until page contains  Successfully delete items
  Wait until keyword succeeds  30  1  Page should not contain Element  css=tr[data-id="foo"] input


should not show warning when deleting page
  Go To  ${PLONE_URL}/foo
  Wait For Then Click Element  css=#plone-contentmenu-actions > a
  Wait For Then Click Element  css=#plone-contentmenu-actions-delete
  Page should not contain element  css=.breach-container .breach-item


remove link to page
  Go To  ${PLONE_URL}/bar
  Wait For Then Click Element  css=#contentview-edit a
  Wait For Element  css=.tox-edit-area iframe
  Select Frame  css=.tox-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame
  Click Button  css=button[aria-label="Remove link"]
  Wait For Then Click Element  css=#form-buttons-save
