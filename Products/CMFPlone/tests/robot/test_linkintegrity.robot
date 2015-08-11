# ============================================================================
# Tests for the Plone Link Integrity Support
# ============================================================================
#
# $ bin/robot-server --reload-path src/Products.CMFPlone/Products/CMFPlone/ Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
#
# $ bin/robot src/Products.CMFPlone/Products/CMFPlone/tests/robot/test_controlpanel_usergroups.robot
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: When page is linked show warning
  Given a logged-in site administrator
    a page to link to
    and a page to edit
    and a link in rich text
    and re-edit the object
    should show warning when deleting page


Scenario: After you fix linked page no longer show warning
  Given a logged-in site administrator
  a page to link to
    and a page to edit
    and a link in rich text
    and re-edit the object
  should show warning when deleting page
    remove link to page
  should not show warning when deleting page


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator


a page to edit
  Go To  ${PLONE_URL}
  Click Link  css=#plone-contentmenu-factories a
  Click Link  css=.plonetoolbar-contenttype .contenttype-document
  Input Text  css=#formfield-form-widgets-IDublinCore-title input  Bar


a page to link to
  Go To  ${PLONE_URL}
  Click Link  css=#plone-contentmenu-factories a
  Click Link  css=.plonetoolbar-contenttype .contenttype-document
  Input Text  css=#formfield-form-widgets-IDublinCore-title input  Foo
  Click Button  css=#form-buttons-save


should show warning when deleting page
  Go To  ${PLONE_URL}/foo
  Click Link  css=#plone-contentmenu-actions a
  Click Link  css=#plone-contentmenu-actions-delete
  Page should contain element  css=.breach-container .breach-item


should not show warning when deleting page
  Go To  ${PLONE_URL}/foo
  Click Link  css=#plone-contentmenu-actions a
  Click Link  css=#plone-contentmenu-actions-delete
  Page should not contain element  css=.breach-container .breach-item

# XXX need to remove this once creation event handling is fixed
re-edit the object
  Go To  ${PLONE_URL}/bar
  Click Link  css=#contentview-edit a
  Click Button  css=#form-buttons-save


a link in rich text
  Select Frame  css=.mce-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame
  Click Button  css=div[aria-label="Insert/edit link"] button
  Click Element  css=.select2-input.select2-default
  Input text  css=.select2-dropdown-open .select2-input  foo
  Click Link  css=.pattern-relateditems-result-select.selectable
  Click Button  css=.plone-modal-footer .plone-btn-primary
  Click Button  css=#form-buttons-save


remove link to page
  Go To  ${PLONE_URL}/bar
  Click Link  css=#contentview-edit a
  Select Frame  css=.mce-edit-area iframe
  Input text  css=.mce-content-body  foo
  Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
  UnSelect Frame
  Click Button  css=div[aria-label="Remove link(s)"] button
  Click Button  css=#form-buttons-save