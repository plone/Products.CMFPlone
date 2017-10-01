*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown


*** Test Cases ***

Show TinyMCE
    Go to  ${PLONE_URL}
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce.png
    ...  css=div.mce-container

Show TinyMCE image
    Go to  ${PLONE_URL}
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-imgbutton.png
    ...  css=#mceu_15

    Click element  css=#mceu_15 button
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-imgdialog.png
    ...  css=div.plone-modal-content

Show TinyMCE insert links
    Go to  ${PLONE_URL}
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-linkbutton.png
    ...  css=#mceu_14

    Click element  css=#mceu_14 button
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-linkdialog.png
    ...  css=div.plone-modal-content

Show TinyMCE insert tables
    Go to  ${PLONE_URL}
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body

    Click element  css=#mceu_21 button
    Mouse over  css=#mceu_44
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-table.png
    ...  css=#content