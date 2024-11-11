*** Settings *****************************************************************

Resource  plone/app/robotframework/browser.robot

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

    Click    //*[@id="form-buttons-save"]
    Get Text    //body    contains    Changes saved


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

an edited page
    Create content  type=Document  title=${TITLE}
    Go to  ${PLONE_URL}/${PAGE_ID}/edit
    Get Text    //body    contains    Edit Page

an uploaded image
    Create content  type=Image  title=an-image

text inserted into wysiwyg
    Fill text to tinymce editor    Susi Sorglos and John Doe

insert link
    Evaluate JavaScript   //div[contains(@class, 'tox-edit-area')]//iframe
    ...    (elem, args) => {
    ...        const iframe_document = elem.contentDocument;
    ...        const body = iframe_document.body;
    ...        const p = body.firstChild;
    ...        const range = new Range();
    ...        range.setStart(p.firstChild, 5);
    ...        range.setEnd(p.firstChild, 12);
    ...        iframe_document.getSelection().removeAllRanges();
    ...        iframe_document.getSelection().addRange(range);
    ...    }
    ...    all_elements=False
    Click    //button[@aria-label='Insert/edit link']
    Wait For Condition    Element States    //div[@class="modal-content"]    contains    visible
    Click    //div[@class="modal-body"]//fieldset[@data-linktype="internal"]//button[contains(@class,"mode") and contains(@class,"browse")]
    Click    //a[@title="Go one level up"]
    Click    //a[contains(@class,"selectable") and @data-path="/test-folder"]
    Click    //div[contains(@class,"modal-footer")]//input[@name="insert"]

insert image
    Click    //button[@aria-label="Insert/edit image"]
    Wait For Condition    Element States    //div[@class="modal-content"]    contains    visible
    Click    //div[@class="modal-body"]//fieldset[@data-linktype="image"]//button[contains(@class,"mode") and contains(@class,"browse")]
    Click    //a[@title="Go one level up"]
    Wait For Condition    Element States    //div[@id="select2-drop"]//ul[@class="select2-results"]    contains    visible
    Click    //div[@id="select2-drop"]//ul[@class="select2-results"]//li/div/div/a[contains(@class,"selectable") and @data-path="/image"]
    Type Text    //div[contains(@class, 'modal-body')]//input[@name="title"]    SomeTitle
    Type Text    //div[contains(@class, 'modal-body')]//input[@name="alt"]    SomeAlt
    Click    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]
