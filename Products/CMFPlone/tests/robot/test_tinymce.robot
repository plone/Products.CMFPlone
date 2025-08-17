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
    Click    css=.linkModal .content-browser-selected-items-wrapper a.btn-primary
    Click item in contenbrowser column    1    3
    Click    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]//button
    Click    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]

insert image
    Click    //button[@aria-label="Insert/edit image"]
    Click    css=.linkModal .content-browser-selected-items-wrapper a.btn-primary
    Click item in contenbrowser column    1    3
    Click    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]//button
    Type Text    //div[contains(@class, 'modal-body')]//input[@name="title"]    SomeTitle
    Type Text    //div[contains(@class, 'modal-body')]//input[@name="alt"]    SomeAlt
    Click    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]
