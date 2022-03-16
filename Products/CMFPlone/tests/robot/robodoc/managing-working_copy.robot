*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Variables ***

@{CONFIGURE_PACKAGES}  plone.app.iterate
@{APPLY_PROFILES}  plone.app.contenttypes:plone-content  plone.app.iterate:default
# ${REGISTER_TRANSLATIONS}  ${CURDIR}/../../_locales

*** Test Cases ***

Show how to checkout
    Go to  ${PLONE_URL}/front-page

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-actions
    Click element  css=span.icon-plone-contentmenu-actions
    Wait until element is visible
    ...  css=#plone-contentmenu-actions li.plone-toolbar-submenu-header

    Mouse over  css=#plone-contentmenu-actions-iterate_checkout
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_checkout.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

Show checkout notification
    Go to  ${PLONE_URL}/front-page

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-actions
    Click element  css=span.icon-plone-contentmenu-actions
    Wait until element is visible
    ...  css=#plone-contentmenu-actions li.plone-toolbar-submenu-header
    Click link  css=#plone-contentmenu-actions-iterate_checkout
    Wait until element is visible
    ...  name=form.button.Checkout
    Click button  name=form.button.Checkout
    Element should be visible  css=.portalMessage
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_checkout-notification.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

Show locked original
    Go to  ${PLONE_URL}/front-page

    Element should be visible  css=#plone-lock-status
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_locked.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

Show check-in option
    Go to  ${PLONE_URL}/copy_of_front-page

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-actions
    Click element  css=span.icon-plone-contentmenu-actions
    Wait until element is visible
    ...  css=#plone-contentmenu-actions li.plone-toolbar-submenu-header

    Mouse over  css=#plone-contentmenu-actions-iterate_checkin
    Update element style  portal-footer  display  none
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_checkin.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

    Click link  css=#plone-contentmenu-actions-iterate_checkin

    Element should be visible  css=#checkin_message
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_checkin-form.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

Show cancel checkout
    Go to  ${PLONE_URL}/copy_of_front-page

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-actions
    Click element  css=span.icon-plone-contentmenu-actions
    Wait until element is visible
    ...  css=#plone-contentmenu-actions li.plone-toolbar-submenu-header

    Mouse over  css=#plone-contentmenu-actions-iterate_checkout_cancel
    Update element style  portal-footer  display  none
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_cancel-checkout.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container

    Click link  css=#plone-contentmenu-actions-iterate_checkout_cancel

    Element should be visible  css=.destructive
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/working-copy_cancel-checkout-form.png
    ...  css=#content-header
    ...  css=div.plone-toolbar-container
