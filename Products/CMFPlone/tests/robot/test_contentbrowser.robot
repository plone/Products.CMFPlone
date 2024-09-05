*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot
Resource  keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Variables  Products/CMFPlone/tests/robot/variables.py

# use this for a ful browser window if you develop the tests
# Test Setup  Run keywords  Plone Test Setup    Maximize Browser Window
Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown

*** Variables ***

${ASSET_FOLDER}    asset-folder
${DOCUMENT_ID}    doc

*** Test cases ***************************************************************


Scenario: Select a related Item
     Given a logged-in site administrator
       and a document
       and a nested asset folder
      When I select a related item image via contentbrowser
      Then a image is selected as related item

Scenario: Select more than one related Items
    Given a logged-in site administrator
      and a document
      and a nested asset folder
     When I select two related item images via contentbrowser
     Then two images are selected as related item

Scenario: add an internal Link via contentbrowser
    Given a logged-in site administrator
      and a document
      and a nested asset folder
     When I set an internal link via contentbrowser
      and I save the document
     Then the document contain the internal link

Scenario: add an image via contentbrowser
    Given a logged-in site administrator
      and a document
      and a nested asset folder
     When I set an image via contentbrowser
      and I save the document
     Then the document contain the image

Scenario: upload an image via contentbrowser
    Given a logged-in site administrator
      and a document
      and a nested asset folder
     When I upload an image via contentbrowser
      and I save the document
     Then the document contain the uploaded image      
      

*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a nested asset folder
    #
    # + Assets
    #  + Mixed
    #   - File1    
    #   - Image1
    #   - Document1
    #   - News Item1
    #   + Files
    #    - File1
    #    - File2
    #    + Images
    #     - Image1
    #     - Image2
    #
    ${folder_assets_uid}=  Create content    type=Folder    title=Assets    id=${ASSET_FOLDER}

    ${folder_mixed_uid}=  Create content    type=Folder    title=Mixed    container=${folder_assets_uid}
    Create content    type=File    title=File1    container=${folder_mixed_uid}
    Create content    type=Image    title=Image1    container=${folder_mixed_uid}
    Create content    type=Document    title=Document1    container=${folder_mixed_uid}
    Create content    type=News Item    title=News Item1    container=${folder_mixed_uid}

    ${folder_files_uid}=  Create content    type=Folder    title=Files    container=${folder_mixed_uid}
    Create content    type=File    title=File1    container=${folder_files_uid}
    Create content    type=File    title=File2    container=${folder_files_uid}
    
    ${folder_images_uid}=  Create content    type=Folder    title=Images    container=${folder_files_uid}
    Create content    type=Image    id=image-1    title=Image1    container=${folder_images_uid}
    Create content    type=Image    id=image-2    title=Image2    container=${folder_images_uid}

a document
    Create content  type=Document  id=${DOCUMENT_ID}    title=My Page

# --- WHEN ------------------------------------------------------------------

I select a related item image via contentbrowser
   Go to  ${PLONE_URL}/${DOCUMENT_ID}/edit
   # Click the Categorization Tab
   Wait For Then Click Element    //a[@id="autotoc-item-autotoc-2"]
   # Click the select button
   Wait For Then Click Element    //div[@id="formfield-form-widgets-IRelatedItems-relatedItems"]//button
   # Click third element in first column, that is the "Assets" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[4]/div[contains(@class, "browseSub")]
   # Click first element in second column, that is the "Mixed" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelItems")]/div[1]/div[contains(@class, "browseSub")]
   # Click fifth element in third column, that is the "Files" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[3]/div[contains(@class, "levelItems")]/div[5]/div[contains(@class, "browseSub")]
   # Click third element in fourth column, that is the "Images" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[4]/div[contains(@class, "levelItems")]/div[3]/div[contains(@class, "browseSub")]
   # Click second element in fifth column, that is the "Image2" Object
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[5]/div[contains(@class, "levelItems")]/div[2]
   # Click the select Button in the Toolbar of column 6
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[6]/div[contains(@class, "levelToolbar")]/button


I select two related item images via contentbrowser
   Go to  ${PLONE_URL}/${DOCUMENT_ID}/edit
   # Click the Categorization Tab
   Wait For Then Click Element    //a[@id="autotoc-item-autotoc-2"]
   # Click the select button
   Wait For Then Click Element    //div[@id="formfield-form-widgets-IRelatedItems-relatedItems"]//button
   # Click third element in first column, that is the "Assets" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[4]/div[contains(@class, "browseSub")]
   # Click first element in second column, that is the "Mixed" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelItems")]/div[1]/div[contains(@class, "browseSub")]
   # Click fifth element in third column, that is the "Files" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[3]/div[contains(@class, "levelItems")]/div[5]/div[contains(@class, "browseSub")]
   # Click third element in fourth column, that is the "Images" folder
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[4]/div[contains(@class, "levelItems")]/div[3]/div[contains(@class, "browseSub")]
   
   # now we select two items in a colum via CTRL+Click
   # Click second element in fifth column, that is the "Image1" Object
   Wait For Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[5]/div[contains(@class, "levelItems")]/div[1]
   Click Element        //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[5]/div[contains(@class, "levelItems")]/div[1]    CTRL
   # Click second element in fifth column, that is the "Image2" Object
   Wait For Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[5]/div[contains(@class, "levelItems")]/div[2]
   Click Element        //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[5]/div[contains(@class, "levelItems")]/div[2]    CTRL
   # Click the select Button in the Toolbar of column 6
   Wait For Then Click Element    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[6]/div[contains(@class, "levelToolbar")]/button


I set an internal link via contentbrowser
    Go to  ${PLONE_URL}/${DOCUMENT_ID}/edit
    Select Frame  css=.tox-edit-area iframe
    Press Keys    //body[@id="tinymce"]    Susi Sorglos and John Doe
    UnSelect Frame
    Execute Javascript    function selectText() {
    ...    var iframe_document = document.querySelector(".tox-edit-area iframe").contentDocument;
    ...    var body = iframe_document.body;
    ...    var p = body.firstChild;
    ...    var range = new Range();
    ...    range.setStart(p.firstChild, 5);
    ...    range.setEnd(p.firstChild, 12);
    ...    iframe_document.getSelection().removeAllRanges();
    ...    iframe_document.getSelection().addRange(range);
    ...    }; selectText();
    Click Button  //button[@aria-label="Insert/edit link"]
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
    Wait Until Element Is Not Visible    xpath=//div[contains(@class,"content-browser-position-wrapper")]
    Wait For Then Click Element    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]

I set an image via contentbrowser
    Go to  ${PLONE_URL}/${DOCUMENT_ID}/edit
    Select Frame  css=.tox-edit-area iframe
    Press Keys    //body[@id="tinymce"]    Susi Sorglos and John Doe
    UnSelect Frame
    Click Button  //button[@aria-label="Insert/edit image"]
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelItems")]/div[1]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[3]/div[contains(@class, "levelItems")]/div[1]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
    Wait Until Element Is Not Visible    xpath=//div[contains(@class,"content-browser-position-wrapper")]
    Wait For Then Click Element    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]

I upload an image via contentbrowser
    Go to  ${PLONE_URL}/${DOCUMENT_ID}/edit
    Select Frame  css=.tox-edit-area iframe
    Press Keys    //body[@id="tinymce"]    Susi Sorglos and John Doe
    UnSelect Frame
    Click Button  //button[@aria-label="Insert/edit image"]
    Wait For Then Click Element  css=.linkModal .content-browser-selected-items-wrapper button.btn-primary
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[1]/div[contains(@class, "levelItems")]/div[3]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelItems")]/div[1]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "toolBar")]/button[contains(@class,"upload")]
    Choose File    xpath=//div[contains(@class,"pat-upload")]//input[@class="dz-hidden-input"]    ${PATH_TO_TEST_FILES}/plone-logo.png
    Wait For Then Click Element  xpath=//div[contains(@class,"pat-upload")]//button[contains(@class,"upload-all")]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[3]/div[contains(@class, "levelItems")]/div[3]
    Wait For Then Click Element  xpath=//div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[contains(@class, "preview")]/div[contains(@class, "levelToolbar")]/button
    Wait Until Element Is Not Visible    xpath=//div[contains(@class,"content-browser-position-wrapper")]
    Wait For Then Click Element    //div[contains(@class, 'modal-footer')]//input[contains(@name, 'insert')]
    Wait Until Element Is Not Visible  css=.modal-footer input[name="insert"]    

I save the document
    Click Button    xpath=//button[@id="form-buttons-save"]



# --- THEN ------------------------------------------------------------------    

a image is selected as related item
    image is releated item    //div[contains(@class, "content-browser-selected-items")]/div[1]/img    /asset-folder/mixed/files/images/image-2/@@images/image/mini    


two images are selected as related item
    image is releated item    //div[contains(@class, "content-browser-selected-items")]/div[1]/img    /asset-folder/mixed/files/images/image-1/@@images/image/mini    
    image is releated item    //div[contains(@class, "content-browser-selected-items")]/div[2]/img    /asset-folder/mixed/files/images/image-2/@@images/image/mini
    
the document contain the internal link
    Element exists    //div[@id="parent-fieldname-text"]//a    href    /plone/doc

the document contain the image
    rendered textfield contain the image with title    Image1

the document contain the uploaded image
    rendered textfield contain the image with title    plone-logo.png


#--- Helper DRY -------------------------------------------------------------

image is releated item
    [arguments]    ${xpath}    ${imagepath}
    Element exists    ${xpath}    src    ${imagepath}

rendered textfield contain the image with title
    [arguments]  ${imagetitle}
    Element exists    //div[@id="parent-fieldname-text"]//picture/img    title    ${imagetitle}

Element exists
    [arguments]  ${xpath}    ${attr}    ${value}
    ${element}=    Set Variable    ${xpath}
    Element Should Be Visible    ${element}
    ${_attr}=  Get Element Attribute    ${element}    ${attr}
    Should End With    ${_attr}    ${value}