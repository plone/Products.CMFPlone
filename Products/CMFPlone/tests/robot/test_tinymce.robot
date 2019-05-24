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

    Click Button  css=#form-buttons-save
    # in FF 34 this fails. in FF46 or chrome this is not a problem at all.
    # remove "Run Keyword And Ignore Error" when https://github.com/plone/jenkins.plone.org/issues/179
    # was solved
    Run Keyword And Ignore Error  Element Should Be Visible  css=#parent-fieldname-text img[alt="SomeAlt"]
    Run Keyword And Ignore Error  Element Should Be Visible  css=#parent-fieldname-text img[title="SomeTitle"]
    Element Should Be Visible  css=#parent-fieldname-text a


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

an edited page
    Create content  type=Document  title=${TITLE}
    Go to  ${PLONE_URL}/${PAGE_ID}/edit
    Wait until page contains  Edit Page

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
    Click Button  css=.pattern-relateditems-container button.favorites
    Click Link  css=.pattern-relateditems-container .favorites a.fav[href='/']
    Wait Until Element Is Visible  css=.pattern-relateditems-result-select.selectable
    Click Link  css=.pattern-relateditems-result-select.selectable
    Input Text  css=.plone-modal-body [name="title"]  SomeTitle
    Click Button  css=.plone-modal-footer .plone-btn-primary
    Select Frame  css=.mce-edit-area iframe
    Execute Javascript  window.getSelection().removeAllRanges()
    UnSelect Frame
    Wait Until Element Is Not Visible  css=.plone-modal-footer .plone-btn-primary

insert image
    Click Button  css=div[aria-label="Insert/edit image"] button
    Click Button  css=.pattern-relateditems-container button.favorites
    Click Link  css=.pattern-relateditems-container .favorites a.fav[href='/']
    Wait Until Element Is Visible  css=.pattern-relateditems-result-select.selectable
    Click Link  css=.pattern-relateditems-result-select.selectable
    Input Text  css=.plone-modal-body [name="title"]  SomeTitle
    Input Text  css=.plone-modal-body [name="alt"]  SomeAlt
    Click Button  css=.plone-modal-footer .plone-btn-primary[name='insert']
    # in FF 34 we need to click twice. in FF46 or chrome this is not a problem at all.
    Run Keyword And Ignore Error  Click Button  css=.plone-modal-footer .plone-btn-primary[name='insert']
    Wait Until Element Is Not Visible  css=.plone-modal-footer .plone-btn-primary[name='insert']
