*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Open SauceLabs test browser  Refresh JS/CSS resources
Test Teardown  Run keywords  Report test status  Close all browsers


*** Variables ****************************************************************

${TITLE}  An edited page
${PAGE_ID}  an-edited-page


*** Test cases ***************************************************************

Scenario: A page is opened to edit
    Given a logged-in site administrator
      and an uploaded image
      and an edited page
      and text inserted into wysiwyg
      and insert link
      and insert image

    Click Button  css=#form-buttons-save
    Element Should Be Visible  css=#parent-fieldname-text img[alt="SomeAlt"]
    Element Should Be Visible  css=#parent-fieldname-text img[title="SomeTitle"]
    Element Should Be Visible  css=#parent-fieldname-text a


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

an edited page
    Create content  type=Document  title=${TITLE}
    Go to  ${PLONE_URL}/${PAGE_ID}/edit

an uploaded image
    Create content  type=Image  title=an-image

text inserted into wysiwyg
    Select Frame  css=.mce-edit-area iframe
    Input text  css=.mce-content-body  foobar
    UnSelect Frame

insert link
    Select Frame  css=.mce-edit-area iframe
    Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
    UnSelect Frame
    Click Button  css=div[aria-label="Insert/edit link"] button
    Click Element  css=.select2-input.select2-default
    Click Link  css=.pattern-relateditems-result-select.selectable
    Input Text  css=.plone-modal-body [name="title"]  SomeTitle
    Click Button  css=.plone-modal-footer .plone-btn-primary
    Select Frame  css=.mce-edit-area iframe
    Execute Javascript  window.getSelection().removeAllRanges()
    UnSelect Frame

insert image
    Click Button  css=div[aria-label="Insert/edit image"] button
    Click Element  css=.select2-input.select2-default
    Click Link  css=.pattern-relateditems-result-select.selectable
    Input Text  css=.plone-modal-body [name="title"]  SomeTitle
    Input Text  css=.plone-modal-body [name="alt"]  SomeAlt
    Click Button  css=.plone-modal-footer .plone-btn-primary
