*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Variables ****************************************************************

${TITLE}  An edited page
${PAGE_ID}  an-edited-page


*** Test cases ***************************************************************

Scenario: A page is opened to edit in TinyMCE
    Given a logged-in site administrator
      and an uploaded image
      and an edited page
      and text inserted into wysiwyg
      and insert link
      and insert image

    Wait For Then Click Element  css=#form-buttons-save
    Wait until page contains  Changes saved


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

an edited page
    Create content  type=Document  title=${TITLE}
    Go to  ${PLONE_URL}/${PAGE_ID}/edit
    Wait until page contains  Edit Page

an uploaded image
    Create content  type=Image  title=an-image

text inserted into wysiwyg
    Wait Until Element Is Visible  css=.tox-edit-area iframe
    Select Frame  css=.tox-edit-area iframe
    Input text  css=.mce-content-body  foobar
    UnSelect Frame

insert link
    Select Frame  css=.tox-edit-area iframe
    Execute Javascript    function selectElementContents(el) {var range = document.createRange(); range.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);} var el = document.getElementById("tinymce"); selectElementContents(el);
    UnSelect Frame
    Click Button  css=button[aria-label="Insert/edit link"]
    Click Button  css=.pat-relateditems-container button.favorites
    Click Link  css=.pat-relateditems-container .favorites a.fav[href='/']
    Wait Until Element Is Visible  css=.pat-relateditems-result-select.selectable
    Click Link  css=.pat-relateditems-result-select.selectable
    Click Button  css=.modal-footer input[name="insert"]
    Select Frame  css=.tox-edit-area iframe
    Execute Javascript  window.getSelection().removeAllRanges()
    UnSelect Frame
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]

insert image
    Click Button  css=button[aria-label="Insert/edit image"]
    Click Button  css=.pat-relateditems-container button.favorites
    Click Link  css=.pat-relateditems-container .favorites a.fav[href='/']
    Wait Until Element Is Visible  css=.pat-relateditems-result-select.selectable
    Click Link  css=.pat-relateditems-result-select.selectable
    Input Text  css=.modal-body [name="title"]  SomeTitle
    Input Text  css=.modal-body [name="alt"]  SomeAlt
    Click Button  css=.modal-footer input[name="insert"]
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]
