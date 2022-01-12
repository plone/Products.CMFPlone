*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown


*** Test Cases ***

Create sample content
    Go to  ${PLONE_URL}

    ${item} =  Create content  type=Document
    ...  id=samplepage  title=Sample Page
    ...  description=The long wait is now over
    ...  text=<p>Our new site is built with Plone.</p>


Show TinyMCE
    Go to  ${PLONE_URL}/samplepage
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Click element  css=#mceu_2-open
    Click element  css=#mceu_2-open
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce.png
    ...  css=#mceu_16

Show TinyMCE image
    Go to  ${PLONE_URL}/samplepage
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-imgbutton.png
    ...  css=#mceu_15

    Click element  css=#mceu_15 button
    Wait until element is visible
    ...  css=h2.modal-title
    Wait until element is visible
    ...  css=div.common-controls

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-imgdialog.png
    ...  css=div.outer-wrapper
    ...  css=div.modal-content

Show TinyMCE insert links
    Go to  ${PLONE_URL}/samplepage
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-linkbutton.png
    ...  css=#mceu_14

    Click element  css=#mceu_14 button
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-linkdialog.png
    ...  css=div.outer-wrapper
    ...  css=div.modal-content

Show TinyMCE insert tables
    Go to  ${PLONE_URL}/samplepage
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body

    Click element  css=#mceu_22-open
    Click element  css=#mceu_42-text
    Wait until element is visible
    ...  css=#mceu_42-text
    Mouse over  css=#mceu_42-text
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-table.png
    ...  css=div.outer-wrappper