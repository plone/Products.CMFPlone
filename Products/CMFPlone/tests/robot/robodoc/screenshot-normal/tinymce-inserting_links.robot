===============
Inserting Links
===============

.. include:: _robot.rst

.. code:: robotframework
   :class: hidden

   *** Test Cases ***

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

Select a word or phrase and click on the *Insert/edit link* icon:

.. figure:: /_robot/tinymce-linkbutton.png
   :align: center
   :alt: TinyMCE link button

The Link dialog will appear:


.. figure:: /_robot/tinymce-linkdialog.png
   :align: center
   :alt: TinyMCE link dialog

Here, you can fill in the information on where you want to link to:

Internal Link
=============

You can search for, or navigate to, the content item that you want to link to. Furthermore, you can set a "target": open in the same browser window, or a new one. In general, it is considered good etiquette to always open internal links in the same window. Setting a descriptive Title for the link is helpful if the item you are linking to does not have a distinctive title of its own.


Upload
======

The Upload tab lets you upload a PDF or Office document or other file. It will be stored in the same Folder as the content item you are editing.

External Link
=============

When linking to external sites, make sure you include the *complete* link, including the "http\/\/" or "https:\/\/" part, otherwise it will be interpreted as a *relative* link within your own site. Again, you can set a Target and Title.
Opinions differ on whether you should open an external link in a new window or not; ask if your organisation has a policy on this.


Email
=====

This tab lets you create a ``mailto:`` link, which will open in the user's email program. You can optionally set a subject for the email, although your visitor will always be able to override it. setting the Email Subject is more a helpful suggestion.


Anchors
=======

Anchors are like position markers within a document, based on headings, subheadings, or another style set within the document. You can also set Anchors at arbitrary positions in a document.
Plone automatically creates Anchors for headings and subheadings, and thus you can directly link to a chapter in a long web document.
