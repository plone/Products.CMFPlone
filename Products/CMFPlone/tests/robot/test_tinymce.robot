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
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
    Wait For Then Click Element  css=.modal-footer input[name="insert"]
    Select Frame  css=.tox-edit-area iframe
    Execute Javascript  window.getSelection().removeAllRanges()
    UnSelect Frame
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]

insert image
    Click Button  css=button[aria-label="Insert/edit image"]
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper .selected-item .item-info button.btn-link
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
    Capture Page Screenshot
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
    Input Text  css=.modal-body [name="title"]  SomeTitle
    Input Text  css=.modal-body [name="alt"]  SomeAlt
    Click Button  css=.modal-footer input[name="insert"]
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]
