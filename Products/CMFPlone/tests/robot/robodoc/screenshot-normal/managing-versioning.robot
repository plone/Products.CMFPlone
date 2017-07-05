Versioning
===============

An overview on how to view the version history of an item, compare versions, preview previous versions and revert to previous versions.

Creating a new version
--------------------------

Plone includes a versioning feature.
By default, the following content types have versioning enabled:

-  Pages
-  News Items
-  Events
-  Links

Note that all other content types do track workflow history (so, when an item was published, unpublished etcetera)

Content items can be configured to have versioning enabled/disabled through the Site Setup Plone Configuration panel under "Types".

When editing an item, you may use the **change note** field at the bottom; the change note will be stored in the item's version history.
If the change note is left blank, Plone includes a default note: "Initial Revision".

A new version is created every time the item is saved.
Versioning keeps track of all kinds of edits: content, metadata, settings, etc.

Viewing the version history
---------------------------

Once an item has been saved, you can see the **History** by clicking on the *clock* item in the Toolbar.

.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

   Create sample content
       Go to  ${PLONE_URL}

       ${item} =  Create content  type=Document
       ...  id=samplepage  title=Sample Page
       ...  description=The long wait is now over
       ...  text=<p>Our new site is built with Plone.</p>
       Fire transition  ${item}  publish

       Go to  ${PLONE_URL}/samplepage
       Click element  css=#contentview-edit a
       Click element  css=#form-widgets-IDublinCore-title
       Input text  css=#form-widgets-IDublinCore-title  Hurray
       Click element  css=#form-widgets-IVersionable-changeNote
       Input text  css=#form-widgets-IVersionable-changeNote  Title should be Hurray, not Sample Page.
       Click button  css=#form-buttons-save

   Show history
       Go to  ${PLONE_URL}/samplepage
       Click link  css=#contentview-history a
       Wait until element is visible
       ...  css=#history-list
       Update element style  portal-footer  display  none

       Capture and crop page screenshot
       ...  ${CURDIR}/_robot/content-history.png
               ...  css=#content-header
               ...  css=div.plone-toolbar-container

.. figure:: /_robot/content-history.png
   :align: center
   :alt: History view of a content item



The most recent version is listed first. The History view provides the following information:

-  The type of edit (content or workflow)
-  Which user made the edit
-  What date and time the edit occurred

In the above example, Jane created a Page, then published it. Then, she decided to edit the Page, change it's title and she put in "Title should be Hurray, not Sample Page." in the "Change notes" box.
Here you can see why it's good to put in change notes: you get a good overview of *why* an item was edited.

Comparing versions
------------------

From the History viewlet you can compare any previous version with the current version or any other version with the version just before it.

To compare any previous version with the one just before it, click the *Compare* link located between two adjacent versions in the History overlay.


By clicking this button, you'll see a screen like this one where you can see the differences between the two versions:

You may also compare any previous version to the *current* version by clicking the *Compare to current* link.


Viewing and reverting to previous versions
------------------------------------------

**You can preview any previous version** of a document by clicking the *View* link to the right of any version listed.

**To revert back to a previous version**, click on the *Revert to this revision* button to the right of any version listed.


