*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Enable Visible IDs in the Editing Control Panel
  Given a logged-in site administrator
    and the editing control panel
   When I enable visible ids
   Then I can see an id field in the settings tab when I create a document

Scenario: Disable Standard Editor in the Editing Control Panel
  Given a logged-in site administrator
    and the editing control panel
   When I disable the standard editor
# XXX: This test fails because the TinyMCE 4 widget ignores both the old and
# the new setting.
#   Then I do not see the standard editor when I create a document

Scenario: Enable Link Integrity Check in the Editing Control Panel
  Given a logged-in site administrator
    and the editing control panel
   When I enable link integrity checks
# XXX: This test fails because linkintegrity in Plone 5 is broken.
# See https://github.com/plone/Products.CMFPlone/issues/255 for details.
#   Then I will be warned if I remove a linked document


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

the editing control panel
  Go to  ${PLONE_URL}/@@editing-controlpanel


# --- WHEN -------------------------------------------------------------------

I enable visible ids
  Select Checkbox  form.widgets.visible_ids:list
  Click Button  Save
  Wait until page contains  Changes saved

I disable the standard editor
  Select from list by label  name=form.widgets.default_editor:list  None
  Click Button  Save
  Wait until page contains  Changes saved

I enable link integrity checks
  Select Checkbox  name=form.widgets.enable_link_integrity_checks:list
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

I can see an id field in the settings tab when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Input Text  name=form.widgets.IDublinCore.title  My Document
  Click Link  Settings
  Page should contain element  name=form.widgets.IShortName.id
  Input Text  name=form.widgets.IShortName.id  this-is-my-custom-short-name
  Click Button  Save
  Wait until page contains  Item created
  Location should be  ${PLONE_URL}/this-is-my-custom-short-name/view

I do not see the standard editor when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Page should not contain element  css=.mce-tinymce

I will be warned if I remove a linked document
  ${doc1_uid}=  Create content  id=doc1  type=Document
  ${doc2_uid}=  Create content  id=doc2  type=Document
  Set field value  ${doc1_uid}  text  <p><a href='resolveuid/${doc2_uid}' data-val='${doc2_uid}' data-linktype='internal'>link</a></p>  text/html
