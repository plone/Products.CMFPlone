*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Enable Livesearch in the Search Control Panel
  Given a logged-in site administrator
    and a document 'My Document'
    and the search control panel
   When I enable livesearch
#   Then then searching for 'My Document' will show a live search
# XXX: Not implemented yet. See https://github.com/plone/Products.CMFPlone/issues/176 for details

Scenario: Exclude Content Types from Search
  Given a logged-in site administrator
    and a document 'My Document'
    and the search control panel
   When I exclude the 'Document' type from search
   Then searching for 'My Document' will not return any results


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

the search control panel
  Go to  ${PLONE_URL}/@@search-controlpanel
  Wait until page contains  Search Settings


# --- WHEN -------------------------------------------------------------------

I enable livesearch
  Select Checkbox  form.widgets.enable_livesearch:list
  Click Button  Save
  Wait until page contains  Changes saved

I exclude the '${portal_type}' type from search
  # Make sure we see the checkbox, in expanded in jenkins it gets a bit under the toolbar
  Click Link  css=a.plone-toolbar-logo
  Unselect Checkbox  xpath=//input[@name='form.widgets.types_not_searched:list' and @value='${portal_type}']
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

then searching for 'My Document' will show a live search
  # XXX: Not implemented yet.
  Go to  ${PLONE_URL}
  Wait until page contains element  xpath=//input[@name='SearchableText']
  Input Text  name=SearchableText  My

searching for '${search_term}' will not return any results
  Go to  ${PLONE_URL}/@@search
  Given patterns are loaded
  Wait until page contains  No results were found
  Input Text  xpath=//form[@id='searchform']//input[@name='SearchableText']  ${search_term}
  Submit Form  name=searchform
  Wait until page contains  items matching your search terms
  XPath Should Match X Times  //strong[@id='search-results-number' and contains(.,'0')]  1


